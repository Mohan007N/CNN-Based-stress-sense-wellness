"""
routes/prediction_routes.py — Stress Prediction & Emotion Analysis Routes
==========================================================================
Endpoints:
    POST /api/predict/stress    — Run stress prediction from survey inputs
    POST /api/predict/emotion   — Analyse facial emotion data
    POST /api/predict/emotion/image — Analyse an uploaded face image (DeepFace)
"""

import json
import logging
import os
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models.prediction_model import EmotionLog, Prediction
from services.emotion_service import EmotionService
from services.ml_service import MLService
from services.recommendation_service import RecommendationService
from utils.validators import validate_required_fields

logger = logging.getLogger(__name__)

prediction_bp = Blueprint("prediction", __name__)

# Lazily initialised — created once per process on first use
_ml_service: MLService | None = None
_emotion_service = EmotionService()
_rec_service     = RecommendationService()


def _get_ml_service() -> MLService:
    """Return (or lazily create) the MLService singleton."""
    global _ml_service
    if _ml_service is None:
        _ml_service = MLService(
            model_path  = current_app.config["STRESS_MODEL_PATH"],
            scaler_path = current_app.config["SCALER_PATH"],
        )
    return _ml_service


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/predict/stress
# ──────────────────────────────────────────────────────────────────────────────
@prediction_bp.route("/stress", methods=["POST"])
@jwt_required()
def predict_stress():
    """
    Run stress prediction from user-supplied survey data.

    Request body (JSON):
        sleep_hours       : float  — hours of sleep last night
        working_hours     : float  — hours worked today
        work_pressure     : float  — 1–10 scale
        physical_activity : float  — hours of exercise per week
        remote_work       : bool   — True if working remotely
        emotion_score     : float  — 0–100 (from emotion analysis)
        fatigue_score     : float  — 0–100
        focus_score       : float  — 0–100

    Returns:
        stress_level, stress_score, burnout_risk, wellness_score,
        recommendations, emotional_state
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    # ── Run ML prediction ────────────────────────────────────────────────────
    try:
        ml      = _get_ml_service()
        result  = ml.predict(data)
    except Exception as e:
        logger.error("ML prediction error: %s", e)
        return jsonify({"success": False, "error": "Prediction service unavailable."}), 503

    # ── Generate recommendations ─────────────────────────────────────────────
    recommendations = _rec_service.generate(
        stress_score  = result["stress_score"],
        burnout_risk  = result["burnout_risk"],
        sleep_hours   = float(data.get("sleep_hours", 7)),
        emotion_score = float(data.get("emotion_score", 50)),
    )

    # ── Persist to database ──────────────────────────────────────────────────
    try:
        pred = Prediction(
            user_id           = user_id,
            sleep_hours       = data.get("sleep_hours"),
            working_hours     = data.get("working_hours"),
            work_pressure     = data.get("work_pressure"),
            physical_activity = data.get("physical_activity"),
            remote_work       = bool(data.get("remote_work", False)),
            emotion_score     = data.get("emotion_score"),
            fatigue_score     = data.get("fatigue_score"),
            focus_score       = data.get("focus_score"),
            stress_level      = result["stress_level"],
            stress_score      = result["stress_score"],
            burnout_risk      = result["burnout_risk"],
            wellness_score    = result["wellness_score"],
            recommendations   = json.dumps(recommendations),
        )
        db.session.add(pred)
        db.session.commit()
        logger.info("Prediction saved: user=%s stress=%s", user_id, result["stress_level"])
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to save prediction: %s", e)
        # Don't fail the response — prediction result is still returned

    return jsonify({
        "success":          True,
        "stress_level":     result["stress_level"],
        "stress_score":     result["stress_score"],
        "stress_percentage":result["stress_score"],   # alias for frontend
        "burnout_risk":     result["burnout_risk"],
        "wellness_score":   result["wellness_score"],
        "confidence":       result.get("confidence", 0.75),
        "model_used":       result.get("model_used", "rule-based"),
        "recommendations":  recommendations,
        "prediction_id":    pred.id if 'pred' in dir() else None,
        "timestamp":        datetime.utcnow().isoformat(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/predict/emotion
# ──────────────────────────────────────────────────────────────────────────────
@prediction_bp.route("/emotion", methods=["POST"])
@jwt_required()
def analyze_emotion():
    """
    Analyse facial emotion data submitted as JSON scores.

    Request body (JSON):
        happy    : float  — 0–100
        sad      : float  — 0–100
        angry    : float  — 0–100
        neutral  : float  — 0–100
        fear     : float  — 0–100
        disgust  : float  — 0–100
        surprise : float  — 0–100

    Returns:
        emotion_score, dominant_emotion, fatigue_level, emotional_state
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    # ── Analyse emotions ─────────────────────────────────────────────────────
    result = _emotion_service.process_emotion_scores(data)

    # ── Persist emotion log ──────────────────────────────────────────────────
    try:
        log = EmotionLog(
            user_id          = user_id,
            happy            = data.get("happy", 0.0),
            sad              = data.get("sad", 0.0),
            angry            = data.get("angry", 0.0),
            neutral          = data.get("neutral", 0.0),
            fear             = data.get("fear", 0.0),
            disgust          = data.get("disgust", 0.0),
            surprise         = data.get("surprise", 0.0),
            dominant_emotion = result["dominant_emotion"],
            emotion_score    = result["emotion_score"],
            fatigue_level    = result["fatigue_level"],
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Failed to save emotion log: %s", e)

    return jsonify({
        "success":          True,
        "emotion_score":    result["emotion_score"],
        "dominant_emotion": result["dominant_emotion"],
        "fatigue_level":    result["fatigue_level"],
        "emotional_state":  result["emotional_state"],
        "scores":           result["scores"],
        "timestamp":        datetime.utcnow().isoformat(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/predict/emotion/image
# ──────────────────────────────────────────────────────────────────────────────
@prediction_bp.route("/emotion/image", methods=["POST"])
@jwt_required()
def analyze_emotion_image():
    """
    Analyse a facial image via DeepFace (optional dependency).

    Accepts multipart/form-data with field name 'image'.
    Falls back to JSON emotion scores if DeepFace is not installed.
    """
    user_id = int(get_jwt_identity())

    # ── Validate file upload ─────────────────────────────────────────────────
    if "image" not in request.files:
        return jsonify({"success": False, "error": "No image file uploaded. Field name must be 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No file selected."}), 400

    allowed = current_app.config.get("ALLOWED_EXTENSIONS", {"png", "jpg", "jpeg", "gif", "webp"})
    ext     = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"success": False, "error": f"File type '{ext}' not allowed."}), 400

    # ── Save temporarily ─────────────────────────────────────────────────────
    upload_dir  = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    filename    = f"emotion_{user_id}_{int(datetime.utcnow().timestamp())}.{ext}"
    save_path   = os.path.join(upload_dir, filename)
    file.save(save_path)

    # ── Run DeepFace analysis ────────────────────────────────────────────────
    result = _emotion_service.analyze_image(save_path)

    # Clean up the temp file after analysis
    try:
        os.remove(save_path)
    except OSError:
        pass

    if result is None:
        return jsonify({
            "success": False,
            "error":   "Image analysis unavailable. DeepFace may not be installed.",
            "hint":    "pip install deepface",
        }), 503

    return jsonify({
        "success":          True,
        "emotion_score":    result["emotion_score"],
        "dominant_emotion": result["dominant_emotion"],
        "fatigue_level":    result["fatigue_level"],
        "emotional_state":  result["emotional_state"],
        "scores":           result["scores"],
        "timestamp":        datetime.utcnow().isoformat(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/predict/emotion/cnn
# ──────────────────────────────────────────────────────────────────────────────
@prediction_bp.route("/emotion/cnn", methods=["POST"])
@jwt_required()
def analyze_emotion_cnn():
    """
    Analyze emotion using custom CNN model.
    
    Request body (JSON):
        image: base64 encoded image string
    
    Returns:
        dominant_emotion, confidence, emotions dict
    """
    from services.cnn_emotion_service import get_cnn_emotion_service
    
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    
    # Get CNN service
    cnn_service = get_cnn_emotion_service()
    
    if not cnn_service.is_available():
        return jsonify({
            "success": False,
            "error": "CNN model not available. Train model first: python model/quick_train_cnn.py"
        }), 503
    
    # Get image data
    image_data = data.get('image')
    if not image_data:
        return jsonify({"success": False, "error": "No image data provided"}), 400
    
    # Predict emotion
    result = cnn_service.predict_emotion(image_data)
    
    if result is None:
        return jsonify({"success": False, "error": "Emotion prediction failed"}), 500
    
    # Process emotions for our format
    emotions_processed = _emotion_service.process_emotion_scores({
        'happy': result['emotions'].get('happy', 0),
        'sad': result['emotions'].get('sad', 0),
        'angry': result['emotions'].get('angry', 0),
        'neutral': result['emotions'].get('neutral', 0),
        'fear': result['emotions'].get('fear', 0),
        'disgust': result['emotions'].get('disgust', 0),
        'surprise': result['emotions'].get('surprise', 0),
    })
    
    # Log to database
    try:
        log = EmotionLog(
            user_id=user_id,
            happy=result['emotions'].get('happy', 0),
            sad=result['emotions'].get('sad', 0),
            angry=result['emotions'].get('angry', 0),
            neutral=result['emotions'].get('neutral', 0),
            fear=result['emotions'].get('fear', 0),
            disgust=result['emotions'].get('disgust', 0),
            surprise=result['emotions'].get('surprise', 0),
            dominant_emotion=result['dominant_emotion'],
            emotion_score=emotions_processed['emotion_score'],
            fatigue_level=emotions_processed['fatigue_level'],
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to save CNN emotion log: {e}")
    
    return jsonify({
        "success": True,
        "dominant_emotion": result['dominant_emotion'],
        "confidence": result['confidence'],
        "emotions": result['emotions'],
        "emotion_score": emotions_processed['emotion_score'],
        "fatigue_level": emotions_processed['fatigue_level'],
        "emotional_state": emotions_processed['emotional_state'],
        "model": "CNN",
        "timestamp": datetime.utcnow().isoformat(),
    }), 200


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/predict/history
# ──────────────────────────────────────────────────────────────────────────────
@prediction_bp.route("/history", methods=["GET"])
@jwt_required()
def prediction_history():
    """
    Return the authenticated user's prediction history (most recent first).

    Query params:
        limit : int  — max records to return (default 20, max 100)
        page  : int  — pagination page number (default 1)
    """
    user_id = int(get_jwt_identity())
    limit   = min(int(request.args.get("limit", 20)), 100)
    page    = max(int(request.args.get("page", 1)), 1)

    paginated = (
        Prediction.query
        .filter_by(user_id=user_id)
        .order_by(Prediction.created_at.desc())
        .paginate(page=page, per_page=limit, error_out=False)
    )

    return jsonify({
        "success":  True,
        "total":    paginated.total,
        "page":     page,
        "pages":    paginated.pages,
        "history":  [p.to_dict() for p in paginated.items],
    }), 200
