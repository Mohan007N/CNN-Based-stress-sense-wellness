"""
services/recommendation_service.py — Wellness Recommendation Engine
====================================================================
Generates contextual wellness recommendations based on:
    - stress_score  (0–100)
    - burnout_risk  ('Low' | 'Moderate' | 'High')
    - sleep_hours   (float)
    - emotion_score (0–100)

Returns a prioritised list of actionable recommendation strings.
"""

import random
from typing import List


class RecommendationService:
    """
    Rule-based wellness recommendation engine.
    
    Recommendations are grouped by category (sleep, stress, movement, mental)
    and selected based on the user's current stress/emotion profile.
    """

    # ── Recommendation pools ─────────────────────────────────────────────────
    _SLEEP_RECS = [
        "🌙 Aim for 7–9 hours of sleep tonight. Consistent sleep improves mood and focus.",
        "😴 Try going to bed 30 minutes earlier this week to reset your sleep cycle.",
        "📵 Avoid screens 1 hour before bedtime to improve sleep quality.",
        "🧘 Practice a short 5-minute relaxation routine before sleeping.",
        "☕ Limit caffeine intake after 2 PM to ensure restful sleep.",
    ]

    _HIGH_STRESS_RECS = [
        "⏸️ Take a 10-minute break every 90 minutes to prevent burnout.",
        "🫁 Try the 4-7-8 breathing technique: inhale 4s, hold 7s, exhale 8s.",
        "✍️ Write down your top 3 priorities for today to reduce mental clutter.",
        "🚶 Take a short 5-minute walk away from your desk to reset your mind.",
        "🎵 Listen to calming music or ambient sounds while working.",
        "🤝 Consider talking to a colleague, friend, or counsellor about your workload.",
    ]

    _MODERATE_STRESS_RECS = [
        "🌿 Step outside for 10 minutes of fresh air and natural light.",
        "💧 Drink a glass of water right now — dehydration worsens stress.",
        "📅 Plan your next hour with a simple task list to regain focus.",
        "🧩 Try a 2-minute mindfulness pause — close your eyes and breathe deeply.",
        "🏃 Schedule 20–30 minutes of light exercise today.",
    ]

    _LOW_STRESS_RECS = [
        "✅ Great job! Keep up your healthy habits and routine.",
        "🌟 Your wellness score is looking strong — stay consistent!",
        "📖 Use this calm period to learn something new or upskill.",
        "🎯 Set a meaningful goal for the week while your energy is high.",
    ]

    _BURNOUT_HIGH_RECS = [
        "🚨 Your burnout risk is HIGH. Please consider speaking with HR or a counsellor.",
        "🏖️ Request a day off this week if possible — mental recovery is essential.",
        "🛑 Delegate or defer non-urgent tasks to protect your energy.",
        "❤️ Self-compassion matters. Acknowledge your effort and be kind to yourself.",
    ]

    _EMOTION_RECS = {
        "negative": [
            "💬 Share how you're feeling with someone you trust today.",
            "🌈 Focus on one small positive thing that happened today.",
            "🎨 Engage in a creative hobby for 15 minutes to lift your mood.",
        ],
        "positive": [
            "😊 Your emotional state looks positive — keep doing what works for you!",
            "🌻 Channel your good energy into a challenging task you've been postponing.",
        ],
    }

    _MOVEMENT_RECS = [
        "💪 Do 5 minutes of desk stretches to release physical tension.",
        "🚴 Even a 15-minute walk counts as beneficial physical activity.",
        "🧘 Try a short yoga or stretching session this evening.",
    ]

    # ── Public interface ──────────────────────────────────────────────────────
    def generate(
        self,
        stress_score:  float,
        burnout_risk:  str,
        sleep_hours:   float = 7.0,
        emotion_score: float = 50.0,
        max_recs:      int   = 5,
    ) -> List[str]:
        """
        Generate a prioritised list of wellness recommendations.

        Parameters
        ----------
        stress_score  : float 0–100
        burnout_risk  : 'Low' | 'Moderate' | 'High'
        sleep_hours   : hours of sleep last night
        emotion_score : 0–100 (higher = more positive)
        max_recs      : maximum recommendations to return

        Returns
        -------
        List of recommendation strings (max `max_recs` items).
        """
        recs: List[str] = []

        # ── Burnout-specific (highest priority) ──────────────────────────────
        if burnout_risk == "High":
            recs.extend(random.sample(self._BURNOUT_HIGH_RECS, min(2, len(self._BURNOUT_HIGH_RECS))))

        # ── Stress-level recommendations ─────────────────────────────────────
        if stress_score >= 65:
            recs.extend(random.sample(self._HIGH_STRESS_RECS, min(2, len(self._HIGH_STRESS_RECS))))
        elif stress_score >= 35:
            recs.extend(random.sample(self._MODERATE_STRESS_RECS, min(2, len(self._MODERATE_STRESS_RECS))))
        else:
            recs.extend(random.sample(self._LOW_STRESS_RECS, min(1, len(self._LOW_STRESS_RECS))))

        # ── Sleep recommendations ─────────────────────────────────────────────
        if sleep_hours < 6.5:
            recs.append(random.choice(self._SLEEP_RECS))

        # ── Emotion-based recommendations ────────────────────────────────────
        if emotion_score < 40:
            recs.extend(random.sample(self._EMOTION_RECS["negative"], 1))
        elif emotion_score >= 70:
            recs.extend(random.sample(self._EMOTION_RECS["positive"], 1))

        # ── Always include a movement tip ────────────────────────────────────
        recs.append(random.choice(self._MOVEMENT_RECS))

        # Deduplicate while preserving order
        seen = set()
        unique_recs = []
        for r in recs:
            if r not in seen:
                seen.add(r)
                unique_recs.append(r)

        return unique_recs[:max_recs]
