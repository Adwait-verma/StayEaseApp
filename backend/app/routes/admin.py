from flask import Blueprint, jsonify
from sqlalchemy import func, select

from ..extensions import db
from ..models import Booking, Payment, Property, User
from ..security import require_roles

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/stats")
@require_roles("ADMIN")
def marketplace_stats():
    user_count = db.session.scalar(select(func.count(User.user_id))) or 0
    active_properties = (
        db.session.scalar(
            select(func.count(Property.property_id)).where(Property.is_active.is_(True))
        )
        or 0
    )
    booking_count = db.session.scalar(select(func.count(Booking.booking_id))) or 0
    confirmed_revenue = (
        db.session.scalar(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == "PAID"
            )
        )
        or 0
    )
    status_rows = db.session.execute(
        select(Booking.status, func.count(Booking.booking_id)).group_by(Booking.status)
    ).all()

    return jsonify(
        {
            "users": user_count,
            "activeProperties": active_properties,
            "bookings": booking_count,
            "paidRevenue": float(confirmed_revenue),
            "bookingsByStatus": {status: count for status, count in status_rows},
        }
    )
