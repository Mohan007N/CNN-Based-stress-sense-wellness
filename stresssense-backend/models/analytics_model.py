# ---------------------------------------------------------------------------
# Database Models — Analytics
# ---------------------------------------------------------------------------
# models/analytics_model.py
#
# Stores pre-aggregated analytics snapshots (daily / weekly) so the
# dashboard does not have to re-compute them on every request.
# ---------------------------------------------------------------------------

from datetime import datetime
from extensions import db


class StressAnalytics(db.Model):
    """Aggregated stress analytics per user per day."""

    __tablename__ = "stress_analytics"

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    # Date of the aggregated period
    period_date    = db.Column(db.Date, nullable=False)          # e.g. 2024-07-15
    period_type    = db.Column(db.String(10), default="daily")   # 'daily' | 'weekly'

    # Aggregated metrics
    avg_stress_score    = db.Column(db.Float, default=0.0)
    avg_wellness_score  = db.Column(db.Float, default=0.0)
    avg_emotion_score   = db.Column(db.Float, default=0.0)
    avg_fatigue_score   = db.Column(db.Float, default=0.0)
    avg_sleep_hours     = db.Column(db.Float, default=0.0)
    prediction_count    = db.Column(db.Integer, default=0)

    # Dominant stress level for the period
    dominant_stress_level = db.Column(db.String(20), nullable=True)
    burnout_risk_flag     = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":                    self.id,
            "user_id":               self.user_id,
            "period_date":           self.period_date.isoformat() if self.period_date else None,
            "period_type":           self.period_type,
            "avg_stress_score":      self.avg_stress_score,
            "avg_wellness_score":    self.avg_wellness_score,
            "avg_emotion_score":     self.avg_emotion_score,
            "avg_fatigue_score":     self.avg_fatigue_score,
            "avg_sleep_hours":       self.avg_sleep_hours,
            "prediction_count":      self.prediction_count,
            "dominant_stress_level": self.dominant_stress_level,
            "burnout_risk_flag":     self.burnout_risk_flag,
            "created_at":            self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<StressAnalytics user={self.user_id} "
            f"date={self.period_date} avg_stress={self.avg_stress_score}>"
        )
