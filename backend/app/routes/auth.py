from flask import Blueprint, jsonify
from sqlalchemy import func, select

from ..errors import ApiError
from ..extensions import db, limiter
from ..models import Role, User
from ..security import (
    create_access_token,
    hash_password,
    login_required,
    verify_password,
)
from ..serializers import serialize_user
from ..validation import json_body, optional_text, required_text

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
@limiter.limit("5 per minute")
def register():
    body = json_body()
    full_name = required_text(body, "fullName", max_length=100)
    email = required_text(body, "email", max_length=150).lower()
    password = required_text(body, "password", max_length=128)
    phone = optional_text(body, "phone", max_length=20)
    role_name = str(body.get("role", "GUEST")).upper()

    if role_name not in {"GUEST", "HOST"}:
        raise ApiError("Public registration supports guest or host accounts only")
    if (
        len(password) < 8
        or not any(char.isalpha() for char in password)
        or not any(char.isdigit() for char in password)
    ):
        raise ApiError(
            "Password must contain at least eight characters, a letter, and a number"
        )

    existing = db.session.scalar(select(User).where(func.lower(User.email) == email))
    if existing:
        raise ApiError("An account with that email already exists", 409)

    role = db.session.scalar(select(Role).where(Role.role_name == role_name))
    if role is None:
        raise ApiError("Database roles are not initialized", 503)

    user = User(
        full_name=full_name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        roles=[role],
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(
        {"token": create_access_token(user), "user": serialize_user(user)}
    ), 201


@auth_bp.post("/login")
@limiter.limit("10 per minute")
def login():
    body = json_body()
    email = required_text(body, "email", max_length=150).lower()
    password = required_text(body, "password", max_length=128)

    user = db.session.scalar(select(User).where(func.lower(User.email) == email))
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.password_hash)
    ):
        raise ApiError("Invalid email or password", 401)

    return jsonify({"token": create_access_token(user), "user": serialize_user(user)})


@auth_bp.get("/me")
@login_required
def me():
    from flask import g

    return jsonify({"user": serialize_user(g.current_user)})
