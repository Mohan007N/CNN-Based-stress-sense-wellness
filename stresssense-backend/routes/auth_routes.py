"""
routes/auth_routes.py — Authentication Routes
==============================================
Handles user registration, login, logout, and profile retrieval.

All responses follow the unified JSON format:
    { "success": bool, "message": str, ...payload }
"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from extensions import db
from models.user_model import User
from utils.validators import validate_email, validate_password, validate_required_fields

logger = logging.getLogger(__name__)

# Create a Blueprint — registered in app.py under /api/auth
auth_bp = Blueprint("auth", __name__)


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/auth/register
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user account.

    Request body (JSON):
        full_name  : str  — required
        email      : str  — required, unique
        password   : str  — required, min 6 chars
        department : str  — optional
        position   : str  — optional
        role       : str  — optional ('user' | 'admin'), defaults to 'user'

    Returns 201 on success with access_token and user data.
    """
    data = request.get_json(silent=True)

    # ── Validate presence ────────────────────────────────────────────────────
    error = validate_required_fields(data, ["full_name", "email", "password"])
    if error:
        return jsonify({"success": False, "error": error}), 400

    # ── Validate format ──────────────────────────────────────────────────────
    if not validate_email(data["email"]):
        return jsonify({"success": False, "error": "Invalid email address."}), 400

    pw_error = validate_password(data["password"])
    if pw_error:
        return jsonify({"success": False, "error": pw_error}), 400

    # ── Check uniqueness ─────────────────────────────────────────────────────
    if User.query.filter_by(email=data["email"].lower().strip()).first():
        return jsonify({"success": False, "error": "An account with this email already exists."}), 409

    # ── Create user ──────────────────────────────────────────────────────────
    try:
        user = User(
            full_name  = data["full_name"].strip(),
            email      = data["email"].lower().strip(),
            role       = data.get("role", "user"),
            department = data.get("department", ""),
            position   = data.get("position", ""),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        # Issue tokens immediately upon registration
        access_token  = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        logger.info("New user registered: %s (id=%s)", user.email, user.id)

        return jsonify({
            "success":       True,
            "message":       "Account created successfully! Welcome to StressSense.",
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "user":          user.to_dict(),
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error("Registration failed: %s", e)
        return jsonify({"success": False, "error": "Registration failed. Please try again."}), 500


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/auth/login
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return JWT tokens.

    Request body (JSON):
        email    : str — required
        password : str — required

    Returns 200 with access_token + refresh_token on success.
    """
    data = request.get_json(silent=True)

    error = validate_required_fields(data, ["email", "password"])
    if error:
        return jsonify({"success": False, "error": error}), 400

    # ── Look up user ─────────────────────────────────────────────────────────
    user = User.query.filter_by(email=data["email"].lower().strip()).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    if not user.is_active:
        return jsonify({"success": False, "error": "Your account has been deactivated. Contact support."}), 403

    # ── Update last login timestamp ──────────────────────────────────────────
    user.last_login = datetime.utcnow()
    db.session.commit()

    # ── Issue tokens ─────────────────────────────────────────────────────────
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    logger.info("User logged in: %s (id=%s)", user.email, user.id)

    return jsonify({
        "success":       True,
        "message":       f"Welcome back, {user.full_name}!",
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user":          user.to_dict(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/auth/refresh
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    """
    Issue a new access token using a valid refresh token.
    The Authorization header must carry: Bearer <refresh_token>
    """
    user_id      = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return jsonify({
        "success":      True,
        "access_token": access_token,
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/auth/me
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """
    Return the profile of the currently authenticated user.
    Requires a valid Bearer token in the Authorization header.
    """
    user_id = get_jwt_identity()
    user    = User.query.get(int(user_id))

    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    return jsonify({
        "success": True,
        "user":    user.to_dict(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# PUT /api/auth/profile
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update the authenticated user's profile fields.
    Only non-sensitive fields (name, department, position) can be changed here.

    Request body (JSON): any subset of { full_name, department, position }
    """
    user_id = get_jwt_identity()
    user    = User.query.get(int(user_id))

    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    data = request.get_json(silent=True) or {}

    # Allowed fields for self-update
    if "full_name" in data and data["full_name"].strip():
        user.full_name = data["full_name"].strip()
    if "department" in data:
        user.department = data["department"]
    if "position" in data:
        user.position = data["position"]

    db.session.commit()
    logger.info("User profile updated: id=%s", user.id)

    return jsonify({
        "success": True,
        "message": "Profile updated successfully.",
        "user":    user.to_dict(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/auth/change-password
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """
    Change the authenticated user's password.

    Request body (JSON):
        current_password : str — required
        new_password     : str — required, min 6 chars
    """
    user_id = get_jwt_identity()
    user    = User.query.get(int(user_id))
    data    = request.get_json(silent=True) or {}

    error = validate_required_fields(data, ["current_password", "new_password"])
    if error:
        return jsonify({"success": False, "error": error}), 400

    if not user.check_password(data["current_password"]):
        return jsonify({"success": False, "error": "Current password is incorrect."}), 401

    pw_error = validate_password(data["new_password"])
    if pw_error:
        return jsonify({"success": False, "error": pw_error}), 400

    user.set_password(data["new_password"])
    db.session.commit()

    return jsonify({"success": True, "message": "Password changed successfully."}), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/auth/logout  (client-side token removal)
# ──────────────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout endpoint.

    Note: JWTs are stateless by design. The client must discard the token.
    For production token revocation, add a token blocklist (Redis recommended).
    """
    user_id = get_jwt_identity()
    logger.info("User logged out: id=%s", user_id)

    return jsonify({
        "success": True,
        "message": "Logged out successfully. Please discard your token.",
    }), 200
