from flask import Blueprint, jsonify
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import db

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health():
    database = "up"
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:  # pragma: no cover - requires an unavailable database
        database = "down"
        db.session.rollback()
    status = 200 if database == "up" else 503
    return jsonify(
        {"status": "ok" if status == 200 else "degraded", "database": database}
    ), status
