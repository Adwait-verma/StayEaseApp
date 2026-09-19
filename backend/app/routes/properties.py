import re
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from sqlalchemy import exists, func, select
from sqlalchemy.orm import joinedload, selectinload

from ..errors import ApiError, AuthorizationError
from ..extensions import db
from ..models import AvailabilityWindow, Booking, Property
from ..security import require_roles
from ..serializers import serialize_property
from ..validation import json_body, parse_date, parse_decimal, parse_int, required_text

properties_bp = Blueprint("properties", __name__, url_prefix="/api/properties")


def _property_query():
    return select(Property).options(
        joinedload(Property.host),
        selectinload(Property.images),
        selectinload(Property.amenities),
        selectinload(Property.availability_windows),
    )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:160] or "property"


def _unique_slug(title: str, city: str) -> str:
    base = _slugify(f"{title}-{city}")
    candidate = base
    suffix = 2
    while db.session.scalar(
        select(Property.property_id).where(Property.slug == candidate)
    ):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


@properties_bp.get("")
def list_properties():
    page = parse_int(request.args.get("page", 1), "page", minimum=1)
    per_page = parse_int(
        request.args.get("perPage", 12), "perPage", minimum=1, maximum=50
    )
    statement = _property_query().where(Property.is_active.is_(True))

    city = request.args.get("city", "").strip()
    if city:
        statement = statement.where(func.lower(Property.city).like(f"%{city.lower()}%"))

    guests = request.args.get("guests")
    if guests:
        statement = statement.where(
            Property.capacity >= parse_int(guests, "guests", minimum=1, maximum=50)
        )

    min_price = request.args.get("minPrice")
    if min_price:
        statement = statement.where(
            Property.base_price >= parse_decimal(min_price, "minPrice", minimum=0)
        )

    max_price = request.args.get("maxPrice")
    if max_price:
        statement = statement.where(
            Property.base_price <= parse_decimal(max_price, "maxPrice", minimum=0)
        )

    check_in_raw = request.args.get("checkIn")
    check_out_raw = request.args.get("checkOut")
    if bool(check_in_raw) != bool(check_out_raw):
        raise ApiError("checkIn and checkOut must be provided together")
    if check_in_raw and check_out_raw:
        check_in = parse_date(check_in_raw, "checkIn")
        check_out = parse_date(check_out_raw, "checkOut")
        if check_in >= check_out:
            raise ApiError("Check-out must be after check-in")

        covered = exists().where(
            AvailabilityWindow.property_id == Property.property_id,
            AvailabilityWindow.is_active.is_(True),
            AvailabilityWindow.start_date <= check_in,
            AvailabilityWindow.end_date >= check_out,
        )
        overlapping = exists().where(
            Booking.property_id == Property.property_id,
            Booking.status.in_(("PENDING", "CONFIRMED")),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        statement = statement.where(covered, ~overlapping)

    statement = statement.order_by(
        Property.average_rating.desc(),
        Property.review_count.desc(),
        Property.created_at.desc(),
    )
    pagination = db.paginate(statement, page=page, per_page=per_page, error_out=False)
    return jsonify(
        {
            "items": [serialize_property(item) for item in pagination.items],
            "page": pagination.page,
            "perPage": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }
    )


@properties_bp.get("/<int:property_id>")
def get_property(property_id: int):
    property_ = db.session.scalar(
        _property_query().where(Property.property_id == property_id)
    )
    if property_ is None or not property_.is_active:
        raise ApiError("Property not found", 404)
    return jsonify({"property": serialize_property(property_, include_details=True)})


@properties_bp.post("")
@require_roles("HOST", "ADMIN")
def create_property():
    body = json_body()
    title = required_text(body, "title", max_length=150)
    city = required_text(body, "city", max_length=100)

    property_ = Property(
        host_id=g.current_user.user_id,
        title=title,
        slug=_unique_slug(title, city),
        description=required_text(body, "description", max_length=4000),
        address_line=required_text(body, "addressLine", max_length=255),
        city=city,
        country=str(body.get("country", "India")).strip()[:100] or "India",
        capacity=parse_int(body.get("capacity"), "capacity", minimum=1, maximum=50),
        bedrooms=parse_int(body.get("bedrooms", 1), "bedrooms", minimum=1, maximum=30),
        bathrooms=parse_decimal(body.get("bathrooms", 1), "bathrooms"),
        base_price=parse_decimal(body.get("basePrice"), "basePrice"),
    )
    db.session.add(property_)
    db.session.commit()
    return jsonify(
        {"property": serialize_property(property_, include_details=True)}
    ), 201


@properties_bp.patch("/<int:property_id>")
@require_roles("HOST", "ADMIN")
def update_property(property_id: int):
    property_ = db.session.get(Property, property_id)
    if property_ is None:
        raise ApiError("Property not found", 404)
    if (
        "ADMIN" not in g.current_user.role_names
        and property_.host_id != g.current_user.user_id
    ):
        raise AuthorizationError("Only the property owner can update this listing")

    body = json_body()
    if "title" in body:
        property_.title = required_text(body, "title", max_length=150)
    if "description" in body:
        property_.description = required_text(body, "description", max_length=4000)
    if "basePrice" in body:
        property_.base_price = parse_decimal(body["basePrice"], "basePrice")
    if "capacity" in body:
        property_.capacity = parse_int(
            body["capacity"], "capacity", minimum=1, maximum=50
        )
    if "active" in body:
        property_.is_active = bool(body["active"])

    db.session.commit()
    return jsonify({"property": serialize_property(property_, include_details=True)})


@properties_bp.post("/<int:property_id>/availability")
@require_roles("HOST", "ADMIN")
def add_availability(property_id: int):
    property_ = db.session.get(Property, property_id)
    if property_ is None:
        raise ApiError("Property not found", 404)
    if (
        "ADMIN" not in g.current_user.role_names
        and property_.host_id != g.current_user.user_id
    ):
        raise AuthorizationError("Only the property owner can manage availability")

    body = json_body()
    start_date = parse_date(body.get("startDate"), "startDate")
    end_date = parse_date(body.get("endDate"), "endDate")
    if start_date >= end_date:
        raise ApiError("Availability end date must be after the start date")
    if end_date <= datetime.now(timezone.utc).date():
        raise ApiError("Availability must include a future date")

    window = AvailabilityWindow(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        price_per_night=parse_decimal(body.get("pricePerNight"), "pricePerNight"),
        note=str(body.get("note", "")).strip()[:255] or None,
    )
    db.session.add(window)
    db.session.commit()
    return (
        jsonify(
            {
                "availability": {
                    "id": window.availability_id,
                    "startDate": window.start_date.isoformat(),
                    "endDate": window.end_date.isoformat(),
                    "pricePerNight": float(window.price_per_night),
                    "note": window.note,
                }
            }
        ),
        201,
    )
