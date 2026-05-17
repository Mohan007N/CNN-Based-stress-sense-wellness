"""
routes/admin_routes.py — Admin Panel Routes
============================================
All routes require a valid JWT token AND admin role.

Endpoints:
    GET    /api/admin/users           — List all users
    GET    /api/admin/users/<id>      — Get a specific user
    PUT    /api/admin/users/<id>      — Update user role / status
    DELETE /api/admin/user/<id>       — Delete a user
    GET    /api/admin/stats           — Platform-wide statistics
    GET    /api/admin/predictions     — All predictions (paginated)
"""

import logging
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models.prediction_model import Prediction
from models.user_model import User

logger   = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__)


# ── Admin-only decorator ──────────────────────────────────────────────────────
def admin_required(fn):
    """Decorator: ensures the JWT owner has role='admin'."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user    = User.query.get(user_id)
        if not user or user.role != "admin":
            return jsonify({"success": False, "error": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapper


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/admin/users
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def list_users():
    """
    Return a paginated list of all registered users.

    Query params:
        page  : int  — page number (default 1)
        limit : int  — per-page count (default 20, max 100)
        role  : str  — filter by 'user' | 'admin'
    """
    page  = max(int(request.args.get("page", 1)), 1)
    limit = min(int(request.args.get("limit", 20)), 100)
    role  = request.args.get("role", "").strip()

    query = User.query
    if role in ("user", "admin"):
        query = query.filter_by(role=role)

    paginated = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )

    return jsonify({
        "success": True,
        "total":   paginated.total,
        "page":    page,
        "pages":   paginated.pages,
        "users":   [u.to_dict() for u in paginated.items],
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/admin/users/<id>
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user(user_id):
    """Return full profile of a specific user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404
    return jsonify({"success": True, "user": user.to_dict()}), 200


# ──────────────────────────────────────────────────────────────────────────────
# PUT /api/admin/users/<id>
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
@jwt_required()
@admin_required
def update_user(user_id):
    """
    Update role or active status of a user.

    Body (JSON): { "role": "admin"|"user", "is_active": bool }
    """
    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    data = request.get_json(silent=True) or {}

    if "role" in data and data["role"] in ("user", "admin"):
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    db.session.commit()
    logger.info("Admin updated user id=%s", user_id)

    return jsonify({"success": True, "message": "User updated.", "user": user.to_dict()}), 200


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /api/admin/user/<id>
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/user/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    """
    Permanently delete a user and all their associated predictions.
    Admins cannot delete themselves.
    """
    requester_id = int(get_jwt_identity())
    if requester_id == user_id:
        return jsonify({"success": False, "error": "You cannot delete your own account."}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    db.session.delete(user)
    db.session.commit()
    logger.info("Admin deleted user id=%s", user_id)

    return jsonify({"success": True, "message": f"User {user_id} deleted successfully."}), 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/admin/stats
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/stats", methods=["GET"])
@jwt_required()
@admin_required
def platform_stats():
    """Return platform-wide aggregate statistics for the admin dashboard."""
    total_users       = User.query.count()
    total_predictions = Prediction.query.count()
    active_users      = User.query.filter_by(is_active=True).count()
    admin_users       = User.query.filter_by(role="admin").count()

    high_stress   = Prediction.query.filter_by(stress_level="High").count()
    moderate_stress = Prediction.query.filter_by(stress_level="Moderate").count()
    low_stress    = Prediction.query.filter_by(stress_level="Low").count()

    return jsonify({
        "success": True,
        "stats": {
            "total_users":        total_users,
            "active_users":       active_users,
            "admin_users":        admin_users,
            "total_predictions":  total_predictions,
            "stress_distribution": {
                "high":     high_stress,
                "moderate": moderate_stress,
                "low":      low_stress,
            },
        },
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/admin/predictions
# ──────────────────────────────────────────────────────────────────────────────
@admin_bp.route("/predictions", methods=["GET"])
@jwt_required()
@admin_required
def all_predictions():
    """Return all predictions across all users (paginated)."""
    page  = max(int(request.args.get("page", 1)), 1)
    limit = min(int(request.args.get("limit", 20)), 100)

    paginated = (
        Prediction.query
        .order_by(Prediction.created_at.desc())
        .paginate(page=page, per_page=limit, error_out=False)
    )

    return jsonify({
        "success":     True,
        "total":       paginated.total,
        "page":        page,
        "pages":       paginated.pages,
        "predictions": [p.to_dict() for p in paginated.items],
    }), 200
