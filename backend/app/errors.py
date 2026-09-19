from flask import g, jsonify
from flask_limiter.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .security import AuthenticationError, AuthorizationError


class ApiError(Exception):
    def __init__(
        self, message: str, status_code: int = 400, details: dict | None = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


def register_error_handlers(app) -> None:
    def payload(message: str, *, details: dict | None = None) -> dict:
        return {
            "error": message,
            "details": details or {},
            "requestId": getattr(g, "request_id", None),
        }

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        db.session.rollback()
        return jsonify(payload(error.message, details=error.details)), error.status_code

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error: AuthenticationError):
        db.session.rollback()
        return jsonify(payload(str(error))), 401

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error: AuthorizationError):
        db.session.rollback()
        return jsonify(payload(str(error))), 403

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error: IntegrityError):
        db.session.rollback()
        app.logger.warning("Database integrity error: %s", error)
        return jsonify(payload("That change conflicts with existing data")), 409

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(error: RateLimitExceeded):
        return jsonify(payload(error.description)), 429

    @app.errorhandler(404)
    def handle_not_found(_error):
        return jsonify(payload("Resource not found")), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(_error):
        return jsonify(payload("Method not allowed")), 405
