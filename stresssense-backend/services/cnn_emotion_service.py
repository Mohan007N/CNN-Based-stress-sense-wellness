"""
services/cnn_emotion_service.py — CNN-based Emotion Recognition Service
========================================================================
Uses trained CNN model for facial emotion detection from images.
"""

import os
import logging
import numpy as np
from typing import Optional, Dict
import base64
from io import BytesIO

logger = logging.getLogger(__name__)

# Try to import TensorFlow
try:
    import tensorflow as tf
    from tensorflow import keras
    from PIL import Image
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logger.warning("TensorFlow not available. CNN emotion detection disabled.")


class CNNEmotionService:
    """
    CNN-based emotion recognition service.
    Loads trained model and provides prediction interface.
    """
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_loaded = False
        
        if not TF_AVAILABLE:
            logger.warning("TensorFlow not installed. CNN service disabled.")
            return
        
        # Default model path
        if model_path is None:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(script_dir, 'model', 'emotion_cnn_model.h5')
        
        self.model_path = model_path
        self.emotion_labels = {
            0: "angry",
            1: "disgust",
            2: "fear",
            3: "happy",
            4: "sad",
            5: "surprise",
            6: "neutral"
        }
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the trained CNN model."""
        if not os.path.exists(self.model_path):
            logger.warning(f"CNN model not found at {self.model_path}")
            logger.info("Train a model first: python model/quick_train_cnn.py")
            return
        
        try:
            self.model = keras.models.load_model(self.model_path)
            self.model_loaded = True
            logger.info(f"✅ CNN emotion model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load CNN model: {e}")
            self.model_loaded = False
    
    def preprocess_image(self, image_data) -> Optional[np.ndarray]:
        """
        Preprocess image for CNN prediction.
        
        Parameters
        ----------
        image_data : PIL.Image, numpy array, or base64 string
            Input image
        
        Returns
        -------
        Preprocessed image array (1, 48, 48, 1) or None
        """
        try:
            # Handle different input types
            if isinstance(image_data, str):
                # Base64 encoded image
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(BytesIO(image_bytes))
            elif isinstance(image_data, np.ndarray):
                # NumPy array
                image = Image.fromarray(image_data)
            else:
                # Assume PIL Image
                image = image_data
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize to 48x48
            image = image.resize((48, 48))
            
            # Convert to array and normalize
            img_array = np.array(image).astype('float32') / 255.0
            img_array = img_array.reshape(1, 48, 48, 1)
            
            return img_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def predict_emotion(self, image_data) -> Optional[Dict]:
        """
        Predict emotion from image using CNN.
        
        Parameters
        ----------
        image_data : PIL.Image, numpy array, or base64 string
            Input face image
        
        Returns
        -------
        dict with emotion predictions or None
        {
            'dominant_emotion': str,
            'confidence': float,
            'emotions': dict of {emotion: score}
        }
        """
        if not self.model_loaded:
            logger.warning("CNN model not loaded")
            return None
        
        # Preprocess image
        img_array = self.preprocess_image(image_data)
        if img_array is None:
            return None
        
        try:
            # Predict
            predictions = self.model.predict(img_array, verbose=0)[0]
            
            # Get dominant emotion
            dominant_idx = np.argmax(predictions)
            dominant_emotion = self.emotion_labels[dominant_idx]
            confidence = float(predictions[dominant_idx])
            
            # All emotions with scores
            emotions = {
                self.emotion_labels[i]: float(predictions[i] * 100)
                for i in range(len(predictions))
            }
            
            return {
                'dominant_emotion': dominant_emotion,
                'confidence': confidence,
                'emotions': emotions,
                'model': 'CNN'
            }
            
        except Exception as e:
            logger.error(f"CNN prediction failed: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if CNN service is available."""
        return TF_AVAILABLE and self.model_loaded


# Singleton instance
_cnn_service = None

def get_cnn_emotion_service() -> CNNEmotionService:
    """Get or create CNN emotion service singleton."""
    global _cnn_service
    if _cnn_service is None:
        _cnn_service = CNNEmotionService()
    return _cnn_service
