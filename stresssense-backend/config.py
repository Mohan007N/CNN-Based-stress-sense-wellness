"""
config.py — StressSense Backend Configuration
==============================================
Centralised configuration for all environments.
Switch between Development, Testing, and Production by setting the
FLASK_ENV environment variable.
"""

import os
from datetime import timedelta


# ---------------------------------------------------------------------------
# Base path helpers
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Create folders if they don't exist yet
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Base Config (shared across all environments)
# ---------------------------------------------------------------------------
class Config:
    # ── Flask ────────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "stresssense-super-secret-key-change-in-prod")
    DEBUG = False
    TESTING = False

    # ── Database ─────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(DATABASE_DIR, 'database.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False          # Set True to see raw SQL queries in dev

    # ── JWT ──────────────────────────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwt-stresssense-2024-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = "HS256"

    # ── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # ── File Uploads ─────────────────────────────────────────────────────────
    UPLOAD_FOLDER = UPLOADS_DIR
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

    # ── ML Model Paths ───────────────────────────────────────────────────────
    STRESS_MODEL_PATH = os.path.join(MODEL_DIR, "stress_model.pkl")
    SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

    # ── Email Configuration (Resend API) ─────────────────────────────────────
    RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "re_dhkUgG1m_MhHK9PyTyzrtE3WhCm4U5dqN")
    EMAIL_FROM = os.environ.get("EMAIL_FROM", "hello@stresssense.app")
    SUPPORT_EMAIL = "hello@stresssense.app"
    SUPPORT_PHONE = "+1 (555) 010-2025"
    COMPANY_ADDRESS = "410 Market St, San Francisco, CA"
    
    # ── Developer Info ───────────────────────────────────────────────────────
    DEVELOPER_NAME = "Mohana Krishnan"
    DEVELOPER_EMAIL = "mohankrishnan4099@gmail.com"
    DEVELOPER_PHONE = "+91 8610844594"
    DEVELOPER_LOCATION = "Chennai"
    DEVELOPER_LINKEDIN = "https://www.linkedin.com/in/mohanakrishnan-n-576565312/"

    # ── App Meta ─────────────────────────────────────────────────────────────
    APP_NAME = "StressSense"
    APP_VERSION = "1.0.0"
    API_PREFIX = "/api"


# ---------------------------------------------------------------------------
# Development Config
# ---------------------------------------------------------------------------
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False          # Flip to True for SQL debug logs


# ---------------------------------------------------------------------------
# Testing Config
# ---------------------------------------------------------------------------
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"   # In-memory DB for tests


# ---------------------------------------------------------------------------
# Production Config
# ---------------------------------------------------------------------------
class ProductionConfig(Config):
    DEBUG = False
    # In production always set SECRET_KEY and JWT_SECRET_KEY via env vars!
    SQLALCHEMY_ECHO = False


# ---------------------------------------------------------------------------
# Config selector
# ---------------------------------------------------------------------------
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config():
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config_map.get(env, DevelopmentConfig)
