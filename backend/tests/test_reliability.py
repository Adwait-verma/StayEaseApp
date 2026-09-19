from conftest import auth_header
from test_booking_workflow import (
    _create_booking,
    _create_property_with_availability,
)

from app import create_app
from app.extensions import db


def test_responses_include_request_id_and_security_headers(client):
    response = client.get(
        "/api/live", headers={"X-Request-ID": "portfolio-check-123"}
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "portfolio-check-123"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Cache-Control"] == "no-store"


def test_readiness_checks_database(client):
    response = client.get("/api/ready")

    assert response.status_code == 200
    assert response.get_json() == {"database": "up", "status": "ready"}


def test_payment_request_requires_idempotency_key(client, register):
    property_id, _ = _create_property_with_availability(client, register)
    guest = register("guest@example.test")
    booking = _create_booking(client, guest["token"], property_id).get_json()[
        "booking"
    ]

    response = client.post(
        f"/api/bookings/{booking['id']}/pay",
        headers=auth_header(guest["token"]),
    )

    assert response.status_code == 400
    assert "Idempotency-Key" in response.get_json()["error"]


def test_replayed_payment_returns_original_result(client, register):
    property_id, _ = _create_property_with_availability(client, register)
    guest = register("guest@example.test")
    booking = _create_booking(client, guest["token"], property_id).get_json()[
        "booking"
    ]
    headers = {
        **auth_header(guest["token"]),
        "Idempotency-Key": "same-payment-request-123",
    }

    first = client.post(f"/api/bookings/{booking['id']}/pay", headers=headers)
    replay = client.post(f"/api/bookings/{booking['id']}/pay", headers=headers)

    assert first.status_code == 200
    assert first.headers["Idempotent-Replayed"] == "false"
    assert replay.status_code == 200
    assert replay.headers["Idempotent-Replayed"] == "true"
    assert replay.get_json()["booking"]["payment"]["reference"] == first.get_json()[
        "booking"
    ]["payment"]["reference"]


def test_login_rate_limit_returns_json_error():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "JWT_SECRET": "rate-limit-test-secret",
            "RATELIMIT_ENABLED": True,
            "RATELIMIT_STORAGE_URI": "memory://",
        }
    )
    with application.app_context():
        db.create_all()
    test_client = application.test_client()

    responses = [
        test_client.post(
            "/api/auth/login",
            json={"email": "missing@example.test", "password": "Wrong123!"},
        )
        for _ in range(11)
    ]

    assert responses[-1].status_code == 429
    assert responses[-1].is_json
    assert responses[-1].get_json()["requestId"]

    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
