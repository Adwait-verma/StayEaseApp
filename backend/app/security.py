from __future__ import annotations

import base64
import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, request

from .extensions import db
from .models import User


class AuthenticationError(Exception):
    pass


class AuthorizationError(Exception):
    pass


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32,
    )
    return f"scrypt$16384$8$1${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt, expected = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        calculated = hashlib.scrypt(
            password.encode("utf-8"),
            salt=_decode(salt),
            n=int(n),
            r=int(r),
            p=int(p),
            dklen=len(_decode(expected)),
        )
        return hmac.compare_digest(calculated, _decode(expected))
    except (ValueError, TypeError):
        return False


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"])
    return jwt.encode(
        {
            "sub": str(user.user_id),
            "roles": sorted(user.role_names),
            "iat": now,
            "exp": expires,
        },
        current_app.config["JWT_SECRET"],
        algorithm="HS256",
    )


def _load_authenticated_user() -> User:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise AuthenticationError("A bearer token is required")

    token = header.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET"],
            algorithms=["HS256"],
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("The access token is invalid or expired") from exc

    user = db.session.get(User, user_id)
    if user is None or not user.is_active:
        raise AuthenticationError("The account is unavailable")
    return user


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        g.current_user = _load_authenticated_user()
        return view(*args, **kwargs)

    return wrapped


def require_roles(*allowed_roles: str):
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if not g.current_user.role_names.intersection(allowed_roles):
                raise AuthorizationError("Your account cannot perform this action")
            return view(*args, **kwargs)

        return wrapped

    return decorator
