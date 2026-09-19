from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from conftest import auth_header


def _future_dates() -> tuple[date, date, date]:
    check_in = datetime.now(UTC).date() + timedelta(days=45)
    check_out = check_in + timedelta(days=3)
    availability_end = check_out + timedelta(days=20)
    return check_in, check_out, availability_end


def _create_property_with_availability(client, register) -> tuple[int, str]:
    host = register(
        "host@example.test", role="HOST", full_name="Aarav Sharma"
    )
    host_headers = auth_header(host["token"])
    property_response = client.post(
        "/api/properties",
        headers=host_headers,
        json={
            "title": "Palm Courtyard Villa",
            "description": "A quiet coastal home with a private courtyard.",
            "addressLine": "18 Beach Road",
            "city": "Goa",
            "country": "India",
            "capacity": 4,
            "bedrooms": 2,
            "bathrooms": 2,
            "basePrice": 2400,
        },
    )
    assert property_response.status_code == 201, property_response.get_json()
    property_id = property_response.get_json()["property"]["id"]

    check_in, _, availability_end = _future_dates()
    availability_response = client.post(
        f"/api/properties/{property_id}/availability",
        headers=host_headers,
        json={
            "startDate": (check_in - timedelta(days=5)).isoformat(),
            "endDate": availability_end.isoformat(),
            "pricePerNight": 2000,
            "note": "Test availability",
        },
    )
    assert availability_response.status_code == 201, availability_response.get_json()
    return property_id, host["token"]


def _create_booking(client, token: str, property_id: int):
    check_in, check_out, _ = _future_dates()
    return client.post(
        "/api/bookings",
        headers=auth_header(token),
        json={
            "propertyId": property_id,
            "checkIn": check_in.isoformat(),
            "checkOut": check_out.isoformat(),
            "guestCount": 2,
        },
    )


def test_host_can_publish_and_guest_cannot(client, register):
    property_id, _ = _create_property_with_availability(client, register)
    guest = register("guest@example.test")

    forbidden = client.post(
        "/api/properties",
        headers=auth_header(guest["token"]),
        json={
            "title": "Should Not Exist",
            "description": "Guests cannot publish properties.",
            "addressLine": "Unknown",
            "city": "Delhi",
            "capacity": 2,
            "basePrice": 1000,
        },
    )
    detail = client.get(f"/api/properties/{property_id}")

    assert forbidden.status_code == 403
    assert detail.status_code == 200
    assert detail.get_json()["property"]["city"] == "Goa"


def test_overlapping_booking_is_rejected_and_search_hides_property(client, register):
    property_id, _ = _create_property_with_availability(client, register)
    first_guest = register("first@example.test")
    second_guest = register("second@example.test")

    first_booking = _create_booking(client, first_guest["token"], property_id)
    overlap = _create_booking(client, second_guest["token"], property_id)

    check_in, check_out, _ = _future_dates()
    search = client.get(
        "/api/properties",
        query_string={
            "city": "Goa",
            "guests": 2,
            "checkIn": check_in.isoformat(),
            "checkOut": check_out.isoformat(),
        },
    )

    assert first_booking.status_code == 201
    assert first_booking.get_json()["booking"]["totalAmount"] == 6000
    assert overlap.status_code == 409
    assert "already booked" in overlap.get_json()["error"].lower()
    assert search.status_code == 200
    assert search.get_json()["items"] == []


def test_payment_and_cancellation_refund_the_demo_payment(client, register):
    property_id, _ = _create_property_with_availability(client, register)
    guest = register("guest@example.test")
    booking_response = _create_booking(client, guest["token"], property_id)
    booking_id = booking_response.get_json()["booking"]["id"]

    paid = client.post(
        f"/api/bookings/{booking_id}/pay",
        headers=auth_header(guest["token"]),
    )
    cancelled = client.post(
        f"/api/bookings/{booking_id}/cancel",
        headers=auth_header(guest["token"]),
        json={"reason": "Travel plans changed"},
    )

    assert paid.status_code == 200
    assert paid.get_json()["booking"]["status"] == "CONFIRMED"
    assert paid.get_json()["booking"]["payment"]["status"] == "PAID"
    assert cancelled.status_code == 200
    assert cancelled.get_json()["booking"]["status"] == "CANCELLED"
    assert cancelled.get_json()["booking"]["payment"]["status"] == "REFUNDED"


def test_completed_stay_can_be_reviewed_and_is_visible_to_admin(
    client, register, admin_token
):
    property_id, _ = _create_property_with_availability(client, register)
    guest = register("guest@example.test")
    booking_response = _create_booking(client, guest["token"], property_id)
    booking_id = booking_response.get_json()["booking"]["id"]
    guest_headers = auth_header(guest["token"])

    premature_review = client.post(
        f"/api/bookings/{booking_id}/review",
        headers=guest_headers,
        json={"rating": 5, "comment": "Too early"},
    )
    client.post(f"/api/bookings/{booking_id}/pay", headers=guest_headers)
    completed = client.post(
        f"/api/bookings/{booking_id}/complete",
        headers=auth_header(admin_token),
    )
    reviewed = client.post(
        f"/api/bookings/{booking_id}/review",
        headers=guest_headers,
        json={"rating": 5, "comment": "A smooth and memorable stay."},
    )
    duplicate_review = client.post(
        f"/api/bookings/{booking_id}/review",
        headers=guest_headers,
        json={"rating": 4, "comment": "Second review"},
    )
    stats = client.get("/api/admin/stats", headers=auth_header(admin_token))

    assert premature_review.status_code == 409
    assert completed.status_code == 200
    assert reviewed.status_code == 201
    assert reviewed.get_json()["review"]["rating"] == 5
    assert duplicate_review.status_code == 409
    assert stats.status_code == 200
    assert stats.get_json()["users"] == 3
    assert stats.get_json()["activeProperties"] == 1
    assert stats.get_json()["bookingsByStatus"] == {"COMPLETED": 1}
    assert stats.get_json()["paidRevenue"] == 6000


def test_non_admin_cannot_read_marketplace_stats(client, register):
    guest = register("guest@example.test")

    response = client.get(
        "/api/admin/stats", headers=auth_header(guest["token"])
    )

    assert response.status_code == 403
