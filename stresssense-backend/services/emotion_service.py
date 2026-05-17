# ---------------------------------------------------------------------------
# services/emotion_service.py — Facial Emotion Analysis Service
# ---------------------------------------------------------------------------
# Accepts emotion data from the frontend (or optionally from an image/frame)
# and derives a composite emotion_score + fatigue classification.
#
# DeepFace integration is optional — the service gracefully falls back to
# the scores sent directly from the frontend.
# ---------------------------------------------------------------------------

import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

# Weights that turn individual emotion scores into a single wellness metric.
# Positive emotions raise the score; negative emotions lower it.
EMOTION_WEIGHTS = {
    "happy":    +1.0,
    "neutral":  +0.3,
    "surprise": +0.2,
    "sad":      -0.6,
    "angry":    -0.8,
    "fear":     -0.7,
    "disgust":  -0.5,
}


class EmotionService:
    """
    Processes facial emotion data and produces derived scores.

    Can operate in two modes:
      1. Direct scores  – caller passes a dict of {emotion: score}
      2. Image mode     – caller passes an image path; DeepFace is invoked
    """

    # ── Core scoring ─────────────────────────────────────────────────────────
    def process_emotion_scores(self, scores: dict) -> dict:
        """
        Turn a dict of raw emotion scores (0–100) into derived analytics.

        Parameters
        ----------
        scores : dict
            Keys: happy, sad, angry, neutral, fear, disgust, surprise

        Returns
        -------
        dict with emotion_score, dominant_emotion, fatigue_level, emotional_state
        """
        # Normalise missing keys to 0
        cleaned = {
            emotion: float(scores.get(emotion, 0.0))
            for emotion in EMOTION_WEIGHTS
        }

        # Dominant emotion
        dominant = max(cleaned, key=cleaned.get)

        # Composite score (weighted sum, mapped to 0–100)
        raw_score = sum(
            cleaned[e] * EMOTION_WEIGHTS[e] for e in cleaned
        )
        # raw_score can be in range [-100, +100] — rescale to [0, 100]
        emotion_score = max(0.0, min(100.0, (raw_score + 100) / 2))

        # Fatigue heuristic (high sad + fear + disgust → fatigued)
        fatigue_raw = (
            cleaned["sad"] * 0.4 +
            cleaned["fear"] * 0.3 +
            cleaned["disgust"] * 0.2 +
            cleaned["angry"] * 0.1
        )
        if fatigue_raw < 25:
            fatigue_level = "Low"
        elif fatigue_raw < 55:
            fatigue_level = "Moderate"
        else:
            fatigue_level = "High"

        # Human-readable emotional state
        emotional_state = self._emotional_state_label(dominant, emotion_score)

        return {
            "emotion_score":    round(emotion_score, 2),
            "dominant_emotion": dominant,
            "fatigue_level":    fatigue_level,
            "emotional_state":  emotional_state,
            "scores":           cleaned,
        }

    # ── DeepFace integration (optional) ──────────────────────────────────────
    def analyze_image(self, image_path: str) -> Optional[dict]:
        """
        Use DeepFace to analyse an uploaded image.
        Returns None if DeepFace is not installed.
        """
        try:
            from deepface import DeepFace  # type: ignore
            result = DeepFace.analyze(
                img_path=image_path,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            # DeepFace returns a list when multiple faces found
            if isinstance(result, list):
                result = result[0]

            emotions = result.get("emotion", {})
            # Convert DeepFace percentages to 0–100 range
            return self.process_emotion_scores(emotions)

        except ImportError:
            logger.info("DeepFace not installed; image analysis unavailable.")
            return None
        except Exception as e:
            logger.error(f"DeepFace analysis failed: {e}")
            return None

    # ── Label helper ─────────────────────────────────────────────────────────
    @staticmethod
    def _emotional_state_label(dominant: str, score: float) -> str:
        if score >= 70:
            return "Positive"
        elif score >= 45:
            return "Neutral"
        elif dominant in ("angry", "disgust"):
            return "Frustrated"
        elif dominant == "sad":
            return "Sad / Burned-out"
        elif dominant == "fear":
            return "Anxious"
        else:
            return "Negative"
