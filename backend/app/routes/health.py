from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/live")
def live():
    return jsonify({"status": "ok", "service": "stayease-api"})


def _readiness_response():
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:  # pragma: no cover - requires an unavailable database
        db.session.rollback()
        return jsonify({"status": "not_ready", "database": "down"}), 503
    return jsonify({"status": "ready", "database": "up"}), 200


@health_bp.get("/ready")
def ready():
    return _readiness_response()


@health_bp.get("/health")
def health():
    """Backward-compatible readiness alias."""
    return _readiness_response()
