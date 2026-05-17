"""
utils/validators.py — Input Validation Utilities
=================================================
Reusable validation helpers used across all routes.
All functions return None on success or an error message string on failure.
"""

import re
from typing import Dict, List, Optional


def validate_required_fields(data: Optional[Dict], fields: List[str]) -> Optional[str]:
    """
    Check that all required keys exist and are non-empty in the data dict.

    Returns an error message string, or None if all fields are present.
    """
    if not data:
        return "Request body is missing or not valid JSON."
    for field in fields:
        if field not in data or data[field] is None or str(data[field]).strip() == "":
            return f"Field '{field}' is required."
    return None


def validate_email(email: str) -> bool:
    """
    Basic email format validation using a simple regex pattern.
    Returns True if valid, False otherwise.
    """
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, str(email).strip()))


def validate_password(password: str) -> Optional[str]:
    """
    Validate password strength.

    Rules:
        - Minimum 6 characters
        - At least 1 letter
        - At least 1 number

    Returns error message string, or None if valid.
    """
    pw = str(password)
    if len(pw) < 6:
        return "Password must be at least 6 characters long."
    if not re.search(r"[A-Za-z]", pw):
        return "Password must contain at least one letter."
    if not re.search(r"\d", pw):
        return "Password must contain at least one number."
    return None


def validate_stress_input(data: Dict) -> Optional[str]:
    """
    Validate the numeric stress prediction input fields.

    Returns an error message string, or None if all values are in range.
    """
    ranges = {
        "sleep_hours":       (0, 24),
        "working_hours":     (0, 24),
        "work_pressure":     (1, 10),
        "physical_activity": (0, 24),
        "emotion_score":     (0, 100),
        "fatigue_score":     (0, 100),
        "focus_score":       (0, 100),
    }

    for field, (low, high) in ranges.items():
        if field in data and data[field] is not None:
            try:
                val = float(data[field])
                if not (low <= val <= high):
                    return f"'{field}' must be between {low} and {high}."
            except (TypeError, ValueError):
                return f"'{field}' must be a number."
    return None


def validate_emotion_input(data: Dict) -> Optional[str]:
    """
    Validate facial emotion score inputs (each must be 0–100).
    """
    emotion_keys = ["happy", "sad", "angry", "neutral", "fear", "disgust", "surprise"]
    for key in emotion_keys:
        if key in data and data[key] is not None:
            try:
                val = float(data[key])
                if not (0 <= val <= 100):
                    return f"Emotion score '{key}' must be between 0 and 100."
            except (TypeError, ValueError):
                return f"Emotion score '{key}' must be a number."
    return None
