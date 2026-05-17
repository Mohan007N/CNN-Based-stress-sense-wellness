"""
routes/dashboard_routes.py — Dashboard & Analytics Routes
==========================================================
Endpoints:
    GET /api/dashboard/analytics      — Stress trend data (Chart.js ready)
    GET /api/dashboard/history        — User prediction history with filters
    GET /api/dashboard/summary        — Weekly wellness summary card data
    GET /api/dashboard/mood-trend     — 7-day mood/emotion trend
    GET /api/dashboard/burnout-stats  — Burnout risk distribution
    GET /api/dashboard/wellness-report— Full weekly wellness report
"""

import logging
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.prediction_model import EmotionLog, Prediction
from services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

dashboard_bp   = Blueprint("dashboard", __name__)
_analytics_svc = AnalyticsService()


@dashboard_bp.route("/analytics", methods=["GET"])
@jwt_required()
def analytics():
    """Return stress & wellness trend data for Chart.js line/bar charts."""
    user_id = int(get_jwt_identity())
    days    = min(int(request.args.get("days", 30)), 365)
    data    = _analytics_svc.get_stress_trend(user_id=user_id, days=days)
    return jsonify({"success": True, **data}), 200


@dashboard_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    """Return paginated prediction history with optional stress_level filter."""
    user_id       = int(get_jwt_identity())
    limit         = min(int(request.args.get("limit", 10)), 50)
    page          = max(int(request.args.get("page", 1)), 1)
    stress_filter = request.args.get("stress_level", "").strip()

    query = Prediction.query.filter_by(user_id=user_id)
    if stress_filter in ("Low", "Moderate", "High"):
        query = query.filter_by(stress_level=stress_filter)

    paginated = query.order_by(Prediction.created_at.desc()).paginate(
        page=page, per_page=limit, error_out=False
    )
    return jsonify({
        "success": True,
        "total":   paginated.total,
        "page":    page,
        "pages":   paginated.pages,
        "history": [p.to_dict() for p in paginated.items],
    }), 200


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    """Return high-level weekly wellness summary for stat cards."""
    user_id = int(get_jwt_identity())
    data    = _analytics_svc.get_weekly_summary(user_id=user_id)
    return jsonify({"success": True, **data}), 200


@dashboard_bp.route("/mood-trend", methods=["GET"])
@jwt_required()
def mood_trend():
    """Return N-day emotion/mood trend for radar or line charts."""
    user_id = int(get_jwt_identity())
    days    = int(request.args.get("days", 7))
    since   = datetime.utcnow() - timedelta(days=days)

    logs = (
        EmotionLog.query
        .filter(EmotionLog.user_id == user_id, EmotionLog.created_at >= since)
        .order_by(EmotionLog.created_at.asc())
        .all()
    )
    trend = _analytics_svc.build_mood_trend(logs, days=days)
    return jsonify({"success": True, "days": days, "trend": trend}), 200


@dashboard_bp.route("/burnout-stats", methods=["GET"])
@jwt_required()
def burnout_stats():
    """Return burnout risk distribution for pie/doughnut charts."""
    user_id = int(get_jwt_identity())
    days    = int(request.args.get("days", 30))
    since   = datetime.utcnow() - timedelta(days=days)

    preds  = Prediction.query.filter(
        Prediction.user_id == user_id,
        Prediction.created_at >= since,
    ).all()

    counts = {"Low": 0, "Moderate": 0, "High": 0}
    for p in preds:
        if p.burnout_risk in counts:
            counts[p.burnout_risk] += 1

    total = sum(counts.values())
    return jsonify({
        "success": True,
        "total":   total,
        "data": {
            "labels":      list(counts.keys()),
            "values":      list(counts.values()),
            "percentages": [
                round((v / total * 100), 1) if total > 0 else 0
                for v in counts.values()
            ],
        },
    }), 200


@dashboard_bp.route("/wellness-report", methods=["GET"])
@jwt_required()
def wellness_report():
    """Generate a full weekly wellness report with insights and tips."""
    user_id = int(get_jwt_identity())
    report  = _analytics_svc.generate_wellness_report(user_id=user_id)
    return jsonify({"success": True, "report": report}), 200
