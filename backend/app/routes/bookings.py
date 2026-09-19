from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from flask import Blueprint, g, jsonify
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..errors import ApiError, AuthorizationError
from ..extensions import db
from ..models import AvailabilityWindow, Booking, Payment, Property, Review
from ..security import login_required, require_roles
from ..serializers import serialize_booking, serialize_review
from ..validation import json_body, optional_text, parse_date, parse_int

bookings_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")
ACTIVE_BOOKING_STATUSES = ("PENDING", "CONFIRMED")


def _booking_query():
    return select(Booking).options(
        selectinload(Booking.property).selectinload(Property.images),
        selectinload(Booking.payment),
        selectinload(Booking.review),
    )


def _load_booking(booking_id: int) -> Booking:
    booking = db.session.scalar(
        _booking_query().where(Booking.booking_id == booking_id)
    )
    if booking is None:
        raise ApiError("Booking not found", 404)
    return booking


@bookings_bp.post("")
@require_roles("GUEST")
def create_booking():
    body = json_body()
    property_id = parse_int(body.get("propertyId"), "propertyId", minimum=1)
    check_in = parse_date(body.get("checkIn"), "checkIn")
    check_out = parse_date(body.get("checkOut"), "checkOut")
    guest_count = parse_int(body.get("guestCount"), "guestCount", minimum=1, maximum=50)

    if check_in < datetime.now(timezone.utc).date():
        raise ApiError("Check-in cannot be in the past")
    if check_in >= check_out:
        raise ApiError("Check-out must be after check-in")

    # Locking the property serializes all booking attempts for this listing.
    property_ = db.session.scalar(
        select(Property)
        .where(Property.property_id == property_id, Property.is_active.is_(True))
        .with_for_update()
    )
    if property_ is None:
        raise ApiError("Property is unavailable", 404)
    if property_.host_id == g.current_user.user_id:
        raise ApiError("Hosts cannot book their own property")
    if guest_count > property_.capacity:
        raise ApiError("Guest count exceeds property capacity")

    availability = db.session.scalar(
        select(AvailabilityWindow)
        .where(
            AvailabilityWindow.property_id == property_id,
            AvailabilityWindow.is_active.is_(True),
            AvailabilityWindow.start_date <= check_in,
            AvailabilityWindow.end_date >= check_out,
        )
        .order_by(
            AvailabilityWindow.price_per_night, AvailabilityWindow.availability_id
        )
        .limit(1)
        .with_for_update()
    )
    if availability is None:
        raise ApiError("No availability covers the requested dates", 409)

    overlap = db.session.scalar(
        select(Booking.booking_id)
        .where(
            Booking.property_id == property_id,
            Booking.status.in_(ACTIVE_BOOKING_STATUSES),
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
        .limit(1)
    )
    if overlap is not None:
        raise ApiError("Property is already booked for those dates", 409)

    total_nights = (check_out - check_in).days
    total_amount = Decimal(availability.price_per_night) * total_nights
    booking = Booking(
        guest_id=g.current_user.user_id,
        property_id=property_id,
        check_in=check_in,
        check_out=check_out,
        guest_count=guest_count,
        nightly_rate=availability.price_per_night,
        total_nights=total_nights,
        total_amount=total_amount,
        status="PENDING",
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify(
        {"booking": serialize_booking(_load_booking(booking.booking_id))}
    ), 201


@bookings_bp.get("")
@login_required
def list_bookings():
    statement = _booking_query()
    roles = g.current_user.role_names
    if "ADMIN" in roles:
        pass
    elif "HOST" in roles:
        statement = statement.join(Property).where(
            Property.host_id == g.current_user.user_id
        )
    else:
        statement = statement.where(Booking.guest_id == g.current_user.user_id)

    bookings = (
        db.session.scalars(statement.order_by(Booking.created_at.desc())).unique().all()
    )
    return jsonify({"items": [serialize_booking(booking) for booking in bookings]})


@bookings_bp.post("/<int:booking_id>/pay")
@require_roles("GUEST")
def pay_for_booking(booking_id: int):
    booking = _load_booking(booking_id)
    if booking.guest_id != g.current_user.user_id:
        raise AuthorizationError("You can only pay for your own booking")
    if booking.status != "PENDING":
        raise ApiError("Only pending bookings can be paid", 409)
    if booking.payment is not None:
        raise ApiError("This booking already has a payment", 409)

    payment = Payment(
        booking_id=booking.booking_id,
        amount=booking.total_amount,
        status="PENDING",
        provider_reference=f"DEMO-{uuid4().hex[:16].upper()}",
    )
    db.session.add(payment)
    db.session.flush()
    payment.status = "PAID"
    payment.paid_at = datetime.now(timezone.utc)
    booking.status = "CONFIRMED"
    db.session.commit()
    return jsonify({"booking": serialize_booking(_load_booking(booking.booking_id))})


@bookings_bp.post("/<int:booking_id>/cancel")
@login_required
def cancel_booking(booking_id: int):
    booking = _load_booking(booking_id)
    is_admin = "ADMIN" in g.current_user.role_names
    if not is_admin and booking.guest_id != g.current_user.user_id:
        raise AuthorizationError("You can only cancel your own booking")
    if booking.status not in ACTIVE_BOOKING_STATUSES:
        raise ApiError("This booking can no longer be cancelled", 409)

    body = json_body()
    reason = optional_text(body, "reason", max_length=500)
    if not reason:
        raise ApiError("A cancellation reason is required")
    booking.status = "CANCELLED"
    booking.cancellation_reason = reason
    if booking.payment and booking.payment.status == "PAID":
        booking.payment.status = "REFUNDED"
    db.session.commit()
    return jsonify({"booking": serialize_booking(_load_booking(booking.booking_id))})


@bookings_bp.post("/<int:booking_id>/complete")
@require_roles("HOST", "ADMIN")
def complete_booking(booking_id: int):
    booking = _load_booking(booking_id)
    is_admin = "ADMIN" in g.current_user.role_names
    if not is_admin and booking.property.host_id != g.current_user.user_id:
        raise AuthorizationError("Only the property host can complete this stay")
    if booking.status != "CONFIRMED":
        raise ApiError("Only confirmed bookings can be completed", 409)
    if booking.check_out > datetime.now(timezone.utc).date() and not is_admin:
        raise ApiError("A stay cannot be completed before check-out", 409)

    booking.status = "COMPLETED"
    db.session.commit()
    return jsonify({"booking": serialize_booking(_load_booking(booking.booking_id))})


@bookings_bp.post("/<int:booking_id>/review")
@require_roles("GUEST")
def create_review(booking_id: int):
    booking = _load_booking(booking_id)
    if booking.guest_id != g.current_user.user_id:
        raise AuthorizationError("You can only review your own stay")
    if booking.status != "COMPLETED":
        raise ApiError("Only completed stays can be reviewed", 409)
    if booking.review is not None:
        raise ApiError("This stay has already been reviewed", 409)

    body = json_body()
    review = Review(
        booking_id=booking.booking_id,
        guest_id=booking.guest_id,
        property_id=booking.property_id,
        rating=parse_int(body.get("rating"), "rating", minimum=1, maximum=5),
        comment=optional_text(body, "comment", max_length=2000),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"review": serialize_review(review)}), 201
