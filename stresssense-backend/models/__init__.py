# models/__init__.py — marks this directory as a Python package
# Import all models here so SQLAlchemy discovers them when create_all() is called.

from models.user_model       import User           # noqa: F401
from models.prediction_model import Prediction, EmotionLog  # noqa: F401
from models.analytics_model  import StressAnalytics         # noqa: F401
