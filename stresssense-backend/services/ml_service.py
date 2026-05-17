# ---------------------------------------------------------------------------
# services/ml_service.py — Machine Learning Service
# ---------------------------------------------------------------------------
# Handles:
#   • Loading the trained RandomForest model and StandardScaler from disk
#   • Feature preprocessing (missing-value handling, scaling)
#   • Stress-level prediction and confidence scoring
#   • Fallback rule-based scoring when the model file is absent
# ---------------------------------------------------------------------------

import os
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)

# ── Feature column order must match training data ────────────────────────────
FEATURE_COLUMNS = [
    "sleep_hours",       # float  – hours per night
    "working_hours",     # float  – hours per day
    "work_pressure",     # float  – 1–10 scale
    "physical_activity", # float  – hours per week
    "remote_work",       # int    – 0 or 1
    "emotion_score",     # float  – 0–100
    "fatigue_score",     # float  – 0–100
    "focus_score",       # float  – 0–100
]

# ── Default / median values used when a feature is missing ──────────────────
FEATURE_DEFAULTS = {
    "sleep_hours":       7.0,
    "working_hours":     8.0,
    "work_pressure":     5.0,
    "physical_activity": 3.0,
    "remote_work":       0,
    "emotion_score":     50.0,
    "fatigue_score":     40.0,
    "focus_score":       60.0,
}


class MLService:
    """
    Singleton-style service for loading and running the stress ML model.
    
    Usage:
        ml = MLService()
        result = ml.predict(input_dict)
    """

    def __init__(self, model_path: str, scaler_path: str):
        self.model_path  = model_path
        self.scaler_path = scaler_path
        self.model       = None
        self.scaler      = None
        self._load_artifacts()

    # ── Model loading ────────────────────────────────────────────────────────
    def _load_artifacts(self) -> None:
        """Load model and scaler from pickle files if they exist."""
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("✅ Stress model loaded successfully.")
            else:
                logger.warning(
                    f"⚠️  Model not found at {self.model_path}. "
                    "Using rule-based fallback."
                )

            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                logger.info("✅ Scaler loaded successfully.")
            else:
                logger.warning("⚠️  Scaler not found. Raw features will be used.")

        except Exception as e:
            logger.error(f"❌ Failed to load ML artifacts: {e}")

    # ── Feature preprocessing ────────────────────────────────────────────────
    def _preprocess(self, raw: dict) -> np.ndarray:
        """
        Convert raw input dict → cleaned numpy array ready for the model.
        Missing keys are filled with sensible defaults.
        """
        row = []
        for col in FEATURE_COLUMNS:
            val = raw.get(col, FEATURE_DEFAULTS[col])
            # Coerce to float; fall back to default on error
            try:
                val = float(val)
            except (TypeError, ValueError):
                val = float(FEATURE_DEFAULTS[col])
            row.append(val)

        features = np.array(row).reshape(1, -1)

        # Apply scaling if scaler is available
        if self.scaler is not None:
            try:
                features = self.scaler.transform(features)
            except Exception as e:
                logger.warning(f"Scaler transform failed: {e}. Using raw features.")

        return features

    # ── Rule-based fallback prediction ───────────────────────────────────────
    def _rule_based_predict(self, raw: dict) -> dict:
        """
        Simple heuristic scoring when ML model is unavailable.
        Returns the same schema as the ML prediction.
        """
        sleep   = float(raw.get("sleep_hours",       FEATURE_DEFAULTS["sleep_hours"]))
        work    = float(raw.get("working_hours",      FEATURE_DEFAULTS["working_hours"]))
        press   = float(raw.get("work_pressure",      FEATURE_DEFAULTS["work_pressure"]))
        fatigue = float(raw.get("fatigue_score",      FEATURE_DEFAULTS["fatigue_score"]))
        emotion = float(raw.get("emotion_score",      FEATURE_DEFAULTS["emotion_score"]))
        focus   = float(raw.get("focus_score",        FEATURE_DEFAULTS["focus_score"]))
        activity = float(raw.get("physical_activity", FEATURE_DEFAULTS["physical_activity"]))

        # Stress contributors (higher = more stress)
        stress_score = 0.0
        stress_score += max(0, (8 - sleep) * 5)       # sleep deficit
        stress_score += max(0, (work - 8)  * 3)       # overwork
        stress_score += press * 3                      # work pressure
        stress_score += fatigue * 0.4                  # fatigue
        stress_score -= focus   * 0.2                  # good focus lowers stress
        stress_score -= activity * 2                   # physical activity helps
        stress_score -= (emotion / 100) * 10           # positive emotions help

        # Clamp to 0–100
        stress_score = max(0, min(100, stress_score))

        # Categorise
        if stress_score < 35:
            level = "Low"
        elif stress_score < 65:
            level = "Moderate"
        else:
            level = "High"

        burnout_risk  = self._calc_burnout_risk(stress_score, fatigue)
        wellness_score = max(0, 100 - stress_score + (focus * 0.2))
        wellness_score = min(100, wellness_score)

        return {
            "stress_score":    round(stress_score, 2),
            "stress_level":    level,
            "burnout_risk":    burnout_risk,
            "wellness_score":  round(wellness_score, 2),
            "confidence":      0.75,
            "model_used":      "rule-based",
        }

    # ── Burnout risk helper ───────────────────────────────────────────────────
    @staticmethod
    def _calc_burnout_risk(stress_score: float, fatigue_score: float) -> str:
        combined = (stress_score + fatigue_score) / 2
        if combined < 35:
            return "Low"
        elif combined < 65:
            return "Moderate"
        return "High"

    # ── Public predict method ────────────────────────────────────────────────
    def predict(self, raw: dict) -> dict:
        """
        Run the full prediction pipeline.

        Parameters
        ----------
        raw : dict
            Dictionary with keys matching FEATURE_COLUMNS.

        Returns
        -------
        dict with:
            stress_score (float 0–100)
            stress_level (str)
            burnout_risk (str)
            wellness_score (float 0–100)
            confidence (float 0–1)
            model_used (str)
        """
        if self.model is None:
            logger.info("Using rule-based fallback prediction.")
            return self._rule_based_predict(raw)

        try:
            features = self._preprocess(raw)

            # Class probabilities
            proba = self.model.predict_proba(features)[0]
            pred_class = int(self.model.predict(features)[0])

            # Map class index to label
            class_labels = ["Low", "Moderate", "High"]
            stress_level = class_labels[min(pred_class, 2)]

            # Stress score = weighted average of class indices
            stress_score = float(
                proba[0] * 20 + proba[1] * 55 + proba[2] * 90
            )
            confidence = float(max(proba))

            fatigue_score = float(raw.get("fatigue_score", FEATURE_DEFAULTS["fatigue_score"]))
            burnout_risk  = self._calc_burnout_risk(stress_score, fatigue_score)

            focus_score = float(raw.get("focus_score", FEATURE_DEFAULTS["focus_score"]))
            wellness_score = max(0, min(100, 100 - stress_score + focus_score * 0.2))

            return {
                "stress_score":   round(stress_score, 2),
                "stress_level":   stress_level,
                "burnout_risk":   burnout_risk,
                "wellness_score": round(wellness_score, 2),
                "confidence":     round(confidence, 4),
                "model_used":     "RandomForest",
            }

        except Exception as e:
            logger.error(f"ML predict failed: {e}. Falling back to rules.")
            return self._rule_based_predict(raw)
