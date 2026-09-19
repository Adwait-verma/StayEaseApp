from __future__ import annotations

from collections.abc import Callable

import pytest

from app import create_app
from app.extensions import db
from app.models import Role, User
from app.security import hash_password


@pytest.fixture()
def app():
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
            "JWT_SECRET": "test-secret-that-is-long-enough-for-the-suite",
        }
    )

    with application.app_context():
        db.create_all()
        db.session.add_all(
            [Role(role_name=name) for name in ("GUEST", "HOST", "ADMIN")]
        )
        db.session.commit()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def register(client) -> Callable:
    def _register(
        email: str,
        *,
        role: str = "GUEST",
        full_name: str = "Test User",
        password: str = "StrongPass123!",
    ) -> dict:
        response = client.post(
            "/api/auth/register",
            json={
                "fullName": full_name,
                "email": email,
                "password": password,
                "role": role,
            },
        )
        assert response.status_code == 201, response.get_json()
        return response.get_json()

    return _register


@pytest.fixture()
def admin_token(app, client) -> str:
    with app.app_context():
        admin_role = db.session.execute(
            db.select(Role).where(Role.role_name == "ADMIN")
        ).scalar_one()
        admin = User(
            full_name="Test Admin",
            email="admin@example.test",
            password_hash=hash_password("AdminPass123!"),
            roles=[admin_role],
        )
        db.session.add(admin)
        db.session.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.test", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return response.get_json()["token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
