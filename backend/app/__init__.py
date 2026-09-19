from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .config import Config
from .errors import register_error_handlers
from .extensions import db, limiter
from .observability import configure_observability
from .routes import register_blueprints


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    limiter.init_app(app)
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        allow_headers=[
            "Authorization",
            "Content-Type",
            "Idempotency-Key",
            "X-Request-ID",
        ],
        expose_headers=[
            "Idempotent-Replayed",
            "RateLimit-Limit",
            "RateLimit-Remaining",
            "RateLimit-Reset",
            "X-Request-ID",
        ],
    )
    register_blueprints(app)
    register_error_handlers(app)
    configure_observability(app)

    return app
