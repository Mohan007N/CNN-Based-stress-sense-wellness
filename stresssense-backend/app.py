"""
app.py — StressSense Flask Application Entry Point
====================================================
Uses the Application Factory pattern so the app can be created
multiple times (e.g., once for the real server, once for tests)
without clashing global state.

Run locally:
    flask run            (uses FLASK_APP=app.py)
    python app.py        (direct execution, debug mode)

Environment variables:
    FLASK_ENV=development | testing | production
    SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL
"""

import logging
import os

from flask import Flask, jsonify

from config import get_config
from extensions import cors, db, jwt

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Application Factory ───────────────────────────────────────────────────────
def create_app(config_class=None):
    """
    Create and configure the Flask application.

    Parameters
    ----------
    config_class : class, optional
        A config class from config.py. Falls back to get_config() which
        reads the FLASK_ENV environment variable.

    Returns
    -------
    Flask app instance, ready to run.
    """
    app = Flask(__name__)

    # ── Load config ──────────────────────────────────────────────────────────
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # ── Initialise extensions ────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # ── Register Blueprints (routes) ─────────────────────────────────────────
    _register_blueprints(app)

    # ── JWT error handlers ───────────────────────────────────────────────────
    _register_jwt_handlers(app)

    # ── Generic error handlers ───────────────────────────────────────────────
    _register_error_handlers(app)

    # ── Create DB tables on first run ────────────────────────────────────────
    with app.app_context():
        _init_database(app)

    # ── Health-check route ───────────────────────────────────────────────────
    @app.route("/")
    def index():
        """Root health-check — useful for Render / Railway uptime pings."""
        return jsonify({
            "success": True,
            "app":     app.config["APP_NAME"],
            "version": app.config["APP_VERSION"],
            "status":  "running",
            "message": "StressSense API is live 🚀",
        })

    @app.route("/api/health")
    def health():
        """Dedicated health-check endpoint."""
        return jsonify({"status": "ok", "version": app.config["APP_VERSION"]})

    logger.info(
        "✅ %s v%s started in [%s] mode",
        app.config["APP_NAME"],
        app.config["APP_VERSION"],
        os.environ.get("FLASK_ENV", "development"),
    )

    return app


# ── Blueprint registration ────────────────────────────────────────────────────
def _register_blueprints(app: Flask) -> None:
    """Import and register all route blueprints under /api."""
    from routes.auth_routes       import auth_bp
    from routes.prediction_routes import prediction_bp
    from routes.dashboard_routes  import dashboard_bp
    from routes.admin_routes       import admin_bp

    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(prediction_bp,  url_prefix="/api/predict")
    app.register_blueprint(dashboard_bp,   url_prefix="/api/dashboard")
    app.register_blueprint(admin_bp,       url_prefix="/api/admin")

    logger.info("Blueprints registered: auth, prediction, dashboard, admin")


# ── JWT error handlers ────────────────────────────────────────────────────────
def _register_jwt_handlers(app: Flask) -> None:
    """Return clean JSON errors instead of HTML for JWT failures."""

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"success": False, "error": "Token has expired. Please log in again."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"success": False, "error": "Invalid token. Please log in again."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({"success": False, "error": "Authorization token is required."}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        return jsonify({"success": False, "error": "Token has been revoked."}), 401


# ── Generic HTTP error handlers ───────────────────────────────────────────────
def _register_error_handlers(app: Flask) -> None:
    """Return JSON for 404 and 500 instead of HTML pages."""

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Resource not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Internal server error: %s", e)
        return jsonify({"success": False, "error": "Internal server error. Please try again later."}), 500

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({"success": False, "error": "Uploaded file is too large (max 16 MB)."}), 413


# ── Database initialisation ───────────────────────────────────────────────────
def _init_database(app: Flask) -> None:
    """
    Create all tables that don't exist yet.
    Import models HERE (inside app context) to avoid circular-import issues.
    """
    # Importing the models registers them with SQLAlchemy metadata
    from models.user_model       import User          # noqa: F401
    from models.prediction_model import Prediction, EmotionLog  # noqa: F401
    from models.analytics_model  import StressAnalytics         # noqa: F401

    db.create_all()
    logger.info("Database tables verified / created.")


# ── CLI helpers ───────────────────────────────────────────────────────────────
app = create_app()


@app.cli.command("seed-admin")
def seed_admin():
    """
    Flask CLI command — create a default admin user.

    Usage:
        flask seed-admin
    """
    from models.user_model import User

    email = "admin@stresssense.ai"
    if User.query.filter_by(email=email).first():
        print(f"Admin user '{email}' already exists.")
        return

    admin = User(
        full_name="StressSense Admin",
        email=email,
        role="admin",
        department="Engineering",
        position="Platform Administrator",
    )
    admin.set_password("Admin@123!")
    db.session.add(admin)
    db.session.commit()
    print(f"✅ Admin user created: {email} / Admin@123!")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Used only for local development.  In production use gunicorn:
    #   gunicorn app:app --bind 0.0.0.0:5000
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=app.config["DEBUG"],
    )
