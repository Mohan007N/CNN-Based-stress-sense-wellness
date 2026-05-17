# ---------------------------------------------------------------------------
# extensions.py — Shared Flask Extensions
# ---------------------------------------------------------------------------
# Import db, jwt, cors from here to avoid circular imports.
# ---------------------------------------------------------------------------

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db   = SQLAlchemy()
jwt  = JWTManager()
cors = CORS()
