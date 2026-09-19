from conftest import auth_header


def test_registration_returns_identity_and_supports_me(client, register):
    account = register(
        "guest@example.test", full_name="Maya Kapoor", role="GUEST"
    )

    assert account["user"]["email"] == "guest@example.test"
    assert account["user"]["roles"] == ["GUEST"]

    response = client.get("/api/auth/me", headers=auth_header(account["token"]))

    assert response.status_code == 200
    assert response.get_json()["user"]["fullName"] == "Maya Kapoor"


def test_registration_rejects_weak_password_and_duplicate_email(client, register):
    weak = client.post(
        "/api/auth/register",
        json={
            "fullName": "Maya Kapoor",
            "email": "maya@example.test",
            "password": "password",
        },
    )
    assert weak.status_code == 400

    register("maya@example.test")
    duplicate = client.post(
        "/api/auth/register",
        json={
            "fullName": "Another Maya",
            "email": "MAYA@example.test",
            "password": "StrongPass123!",
        },
    )

    assert duplicate.status_code == 409


def test_protected_endpoint_requires_valid_token(client):
    missing = client.get("/api/bookings")
    invalid = client.get(
        "/api/bookings", headers={"Authorization": "Bearer not-a-token"}
    )

    assert missing.status_code == 401
    assert invalid.status_code == 401
