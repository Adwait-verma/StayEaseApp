from .admin import admin_bp
from .auth import auth_bp
from .bookings import bookings_bp
from .docs import docs_bp
from .health import health_bp
from .properties import properties_bp


def register_blueprints(app) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(properties_bp)
    app.register_blueprint(bookings_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(docs_bp)
