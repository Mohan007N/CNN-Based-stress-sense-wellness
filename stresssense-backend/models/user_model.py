# ---------------------------------------------------------------------------
# Database Models — User
# ---------------------------------------------------------------------------
# models/user_model.py
#
# Defines the 'users' table. Each row represents one registered user.
# Passwords are stored as bcrypt hashes — never in plain text.
# ---------------------------------------------------------------------------

from datetime import datetime
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    """SQLAlchemy model for the 'users' table."""

    __tablename__ = "users"

    # ── Primary Key ──────────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Personal Info ────────────────────────────────────────────────────────
    full_name = db.Column(db.String(120), nullable=False)
    email     = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password  = db.Column(db.String(256), nullable=False)   # hashed

    # ── Role & Status ────────────────────────────────────────────────────────
    role       = db.Column(db.String(20), default="user", nullable=False)
    is_active  = db.Column(db.Boolean, default=True)

    # ── Timestamps ───────────────────────────────────────────────────────────
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    last_login  = db.Column(db.DateTime, nullable=True)

    # ── Profile extras ───────────────────────────────────────────────────────
    department  = db.Column(db.String(100), nullable=True)
    position    = db.Column(db.String(100), nullable=True)
    avatar_url  = db.Column(db.String(300), nullable=True)

    # ── Relationships ────────────────────────────────────────────────────────
    # One user → many predictions
    predictions = db.relationship(
        "Prediction", backref="user", lazy=True, cascade="all, delete-orphan"
    )

    # ── Password helpers ─────────────────────────────────────────────────────
    def set_password(self, plain_password: str) -> None:
        """Hash and store a plain-text password."""
        self.password = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """Return True if *plain_password* matches the stored hash."""
        return check_password_hash(self.password, plain_password)

    # ── Serialisation ────────────────────────────────────────────────────────
    def to_dict(self, include_private: bool = False) -> dict:
        """Convert user row to a JSON-serialisable dictionary."""
        data = {
            "id":         self.id,
            "full_name":  self.full_name,
            "email":      self.email,
            "role":       self.role,
            "is_active":  self.is_active,
            "department": self.department,
            "position":   self.position,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        return data

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
