from .models import Booking, Property, Review, User


def serialize_user(user: User) -> dict:
    return {
        "id": user.user_id,
        "fullName": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "roles": sorted(user.role_names),
        "active": user.is_active,
    }


def serialize_property(property_: Property, *, include_details: bool = False) -> dict:
    result = {
        "id": property_.property_id,
        "hostId": property_.host_id,
        "hostName": property_.host.full_name,
        "title": property_.title,
        "slug": property_.slug,
        "description": property_.description,
        "city": property_.city,
        "country": property_.country,
        "capacity": property_.capacity,
        "bedrooms": property_.bedrooms,
        "bathrooms": float(property_.bathrooms),
        "basePrice": float(property_.base_price),
        "averageRating": float(property_.average_rating),
        "reviewCount": property_.review_count,
        "active": property_.is_active,
        "coverImage": property_.images[0].image_url if property_.images else None,
        "amenities": [amenity.amenity_name for amenity in property_.amenities],
    }
    if include_details:
        result["addressLine"] = property_.address_line
        result["images"] = [
            {
                "url": image.image_url,
                "alt": image.alt_text,
                "order": image.display_order,
            }
            for image in property_.images
        ]
        result["availability"] = [
            {
                "id": window.availability_id,
                "startDate": window.start_date.isoformat(),
                "endDate": window.end_date.isoformat(),
                "pricePerNight": float(window.price_per_night),
                "note": window.note,
            }
            for window in property_.availability_windows
            if window.is_active
        ]
    return result


def serialize_review(review: Review) -> dict:
    return {
        "id": review.review_id,
        "bookingId": review.booking_id,
        "guestId": review.guest_id,
        "rating": review.rating,
        "comment": review.comment,
        "createdAt": review.created_at.isoformat(),
    }


def serialize_booking(booking: Booking) -> dict:
    return {
        "id": booking.booking_id,
        "guestId": booking.guest_id,
        "property": {
            "id": booking.property.property_id,
            "title": booking.property.title,
            "city": booking.property.city,
            "coverImage": booking.property.images[0].image_url
            if booking.property.images
            else None,
        },
        "checkIn": booking.check_in.isoformat(),
        "checkOut": booking.check_out.isoformat(),
        "guestCount": booking.guest_count,
        "nightlyRate": float(booking.nightly_rate),
        "totalNights": booking.total_nights,
        "totalAmount": float(booking.total_amount),
        "status": booking.status,
        "cancellationReason": booking.cancellation_reason,
        "payment": None
        if booking.payment is None
        else {
            "status": booking.payment.status,
            "reference": booking.payment.provider_reference,
            "paidAt": booking.payment.paid_at.isoformat()
            if booking.payment.paid_at
            else None,
        },
        "review": serialize_review(booking.review) if booking.review else None,
        "createdAt": booking.created_at.isoformat(),
    }
