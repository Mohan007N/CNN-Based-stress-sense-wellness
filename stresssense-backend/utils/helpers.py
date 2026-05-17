"""
utils/helpers.py — General-purpose Helper Utilities
====================================================
Miscellaneous helpers used across the StressSense backend.
"""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional


def success_response(data: Dict = None, message: str = "Success", status: int = 200):
    """
    Build a standardised success JSON response dict.

    Example:
        return jsonify(success_response({"user": user.to_dict()})), 200
    """
    payload = {"success": True, "message": message}
    if data:
        payload.update(data)
    return payload, status


def error_response(message: str, status: int = 400):
    """
    Build a standardised error JSON response dict.

    Example:
        return jsonify(error_response("Not found.")), 404
    """
    return {"success": False, "error": message}, status


def serialize_datetime(obj: Any) -> str:
    """
    JSON serialiser helper for datetime objects.
    Pass as the default= arg to json.dumps().
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable.")


def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    """
    Safely paginate a SQLAlchemy query.

    Parameters
    ----------
    query       : SQLAlchemy BaseQuery
    page        : requested page (1-indexed)
    per_page    : records per page
    max_per_page: hard cap on records per page

    Returns Flask-SQLAlchemy Pagination object.
    """
    page     = max(1, int(page))
    per_page = min(max(1, int(per_page)), max_per_page)
    return query.paginate(page=page, per_page=per_page, error_out=False)


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp a numeric value to [lo, hi]."""
    return max(lo, min(hi, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float; return default on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def level_from_score(score: float) -> str:
    """
    Map a 0–100 score to a Low / Moderate / High label.

    Used for stress_level and burnout_risk display values.
    """
    if score < 35:
        return "Low"
    elif score < 65:
        return "Moderate"
    return "High"


def build_chart_dataset(
    labels: List[str],
    data: List[Optional[float]],
    label: str,
    color: str = "rgb(99,102,241)",
) -> Dict:
    """
    Build a Chart.js dataset dict for line/bar charts.

    Parameters
    ----------
    labels : list of date/time strings
    data   : list of numeric values
    label  : dataset display label
    color  : CSS colour string

    Returns a Chart.js-compatible dataset dict.
    """
    return {
        "labels": labels,
        "datasets": [{
            "label":           label,
            "data":            data,
            "borderColor":     color,
            "backgroundColor": color.replace("rgb", "rgba").replace(")", ",0.15)"),
            "tension":         0.4,
            "fill":            True,
        }],
    }
