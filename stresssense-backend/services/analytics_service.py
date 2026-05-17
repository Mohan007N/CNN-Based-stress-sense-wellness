"""
services/analytics_service.py — Analytics & Reporting Service
=============================================================
Builds Chart.js-ready data structures from raw database records.
Called by dashboard_routes.py.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from models.prediction_model import EmotionLog, Prediction

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Aggregates prediction data into chart-ready analytics payloads."""

    # ── Stress trend (line/bar chart) ─────────────────────────────────────────
    def get_stress_trend(self, user_id: int, days: int = 30) -> Dict:
        """
        Return daily averaged stress & wellness scores for the past `days` days.
        Compatible with Chart.js line chart data format.
        """
        since = datetime.utcnow() - timedelta(days=days)
        preds = (
            Prediction.query
            .filter(Prediction.user_id == user_id, Prediction.created_at >= since)
            .order_by(Prediction.created_at.asc())
            .all()
        )

        # Group by date string
        buckets: Dict[str, Dict] = {}
        for p in preds:
            key = p.created_at.strftime("%Y-%m-%d")
            if key not in buckets:
                buckets[key] = {"stress": [], "wellness": [], "emotion": []}
            buckets[key]["stress"].append(p.stress_score)
            buckets[key]["wellness"].append(p.wellness_score or 0)
            if p.emotion_score is not None:
                buckets[key]["emotion"].append(p.emotion_score)

        labels         = sorted(buckets.keys())
        stress_data    = [round(sum(buckets[d]["stress"])  / len(buckets[d]["stress"]),  1) for d in labels]
        wellness_data  = [round(sum(buckets[d]["wellness"])/ len(buckets[d]["wellness"]),1) for d in labels]
        emotion_data   = [
            round(sum(buckets[d]["emotion"]) / len(buckets[d]["emotion"]), 1)
            if buckets[d]["emotion"] else None
            for d in labels
        ]

        return {
            "labels":        labels,
            "stress_data":   stress_data,
            "wellness_data": wellness_data,
            "emotion_data":  emotion_data,
            "total_records": len(preds),
            "days":          days,
        }

    # ── Weekly summary card ───────────────────────────────────────────────────
    def get_weekly_summary(self, user_id: int) -> Dict:
        """
        Compute summary statistics for the past 7 days:
        avg stress, avg wellness, dominant stress level, record count.
        """
        since = datetime.utcnow() - timedelta(days=7)
        preds = Prediction.query.filter(
            Prediction.user_id == user_id,
            Prediction.created_at >= since,
        ).all()

        if not preds:
            return {
                "week_records":      0,
                "avg_stress_score":  None,
                "avg_wellness_score":None,
                "dominant_level":    None,
                "burnout_flag":      False,
                "message":           "No data for this week yet. Complete a stress check to get started!",
            }

        avg_stress   = round(sum(p.stress_score for p in preds)             / len(preds), 1)
        avg_wellness = round(sum((p.wellness_score or 0) for p in preds)    / len(preds), 1)

        level_counts = {"Low": 0, "Moderate": 0, "High": 0}
        for p in preds:
            if p.stress_level in level_counts:
                level_counts[p.stress_level] += 1
        dominant_level = max(level_counts, key=level_counts.get)

        burnout_flag = any(p.burnout_risk == "High" for p in preds)

        return {
            "week_records":       len(preds),
            "avg_stress_score":   avg_stress,
            "avg_wellness_score": avg_wellness,
            "dominant_level":     dominant_level,
            "burnout_flag":       burnout_flag,
            "level_distribution": level_counts,
        }

    # ── Mood trend (radar / line chart) ──────────────────────────────────────
    def build_mood_trend(self, logs: List[EmotionLog], days: int = 7) -> List[Dict]:
        """
        Aggregate EmotionLog records into a daily mood summary list.
        Each entry = one day's average emotion scores.
        """
        # Build date → scores mapping
        buckets: Dict[str, Dict[str, List[float]]] = {}
        emotions = ["happy", "sad", "angry", "neutral", "fear", "disgust", "surprise"]

        for log in logs:
            key = log.created_at.strftime("%Y-%m-%d")
            if key not in buckets:
                buckets[key] = {e: [] for e in emotions}
                buckets[key]["emotion_score"] = []
            for e in emotions:
                buckets[key][e].append(getattr(log, e, 0.0) or 0.0)
            if log.emotion_score is not None:
                buckets[key]["emotion_score"].append(log.emotion_score)

        trend = []
        for day_key in sorted(buckets.keys()):
            b = buckets[day_key]
            entry = {"date": day_key}
            for e in emotions:
                vals = b[e]
                entry[e] = round(sum(vals) / len(vals), 1) if vals else 0.0
            scores = b["emotion_score"]
            entry["emotion_score"] = round(sum(scores) / len(scores), 1) if scores else None
            trend.append(entry)

        return trend

    # ── Full wellness report ──────────────────────────────────────────────────
    def generate_wellness_report(self, user_id: int) -> Dict:
        """
        Build a comprehensive weekly wellness report dict.
        """
        summary = self.get_weekly_summary(user_id=user_id)
        trend   = self.get_stress_trend(user_id=user_id, days=7)

        avg_stress = summary.get("avg_stress_score", 0) or 0

        # Simple insight generation
        if avg_stress >= 65:
            insight = "Your stress levels this week have been high. Prioritise rest, boundaries, and support."
        elif avg_stress >= 35:
            insight = "Moderate stress this week. Stay consistent with healthy habits."
        else:
            insight = "Excellent week! Your stress levels are well-managed. Keep it up."

        return {
            "period":       "Last 7 days",
            "generated_at": datetime.utcnow().isoformat(),
            "summary":      summary,
            "trend":        trend,
            "insight":      insight,
        }
