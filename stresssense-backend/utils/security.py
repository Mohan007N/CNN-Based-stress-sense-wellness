"""
utils/security.py — Security Utilities
=======================================
Helper functions for secure operations:
    - Allowed file extension checking
    - Secure filename sanitisation
    - Rate-limit helpers (informational, not enforced here)
"""

import hashlib
import os
from typing import Set

from werkzeug.utils import secure_filename as _werkzeug_secure_filename


def allowed_file(filename: str, allowed_extensions: Set[str] = None) -> bool:
    """
    Return True if the filename has an allowed extension.

    Parameters
    ----------
    filename          : original filename from request.files
    allowed_extensions: set of lowercase extensions without dot,
                        e.g. {'png', 'jpg', 'jpeg'}
    """
    if allowed_extensions is None:
        allowed_extensions = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def safe_filename(filename: str) -> str:
    """
    Return a werkzeug-sanitised filename safe for use on the filesystem.
    Strips path separators and potentially dangerous characters.
    """
    return _werkzeug_secure_filename(filename)


def hash_string(value: str) -> str:
    """
    Return the SHA-256 hex digest of a string.
    Useful for generating consistent identifiers (not for passwords — use werkzeug).
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_upload_filename(user_id: int, original_filename: str) -> str:
    """
    Generate a unique, filesystem-safe filename for an uploaded image.

    Format: upload_<user_id>_<timestamp>.<ext>
    """
    import time
    ext  = original_filename.rsplit(".", 1)[-1].lower() if "." in original_filename else "bin"
    ts   = int(time.time() * 1000)   # millisecond timestamp
    return safe_filename(f"upload_{user_id}_{ts}.{ext}")
