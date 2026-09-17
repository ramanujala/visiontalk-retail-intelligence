import os
from typing import Optional
from app.core.config import settings
from app.services.detection.exceptions import ModelLoadError

# Lazy singleton model reference
_yolo_model_instance = None
_loaded_model_path: Optional[str] = None


def get_yolo_model():
    """Lazy loads and caches the Ultralytics YOLO model singleton instance."""
    global _yolo_model_instance, _loaded_model_path

    model_path = settings.YOLO_MODEL_PATH

    if _yolo_model_instance is not None and _loaded_model_path == model_path:
        return _yolo_model_instance

    try:
        from ultralytics import YOLO
        _yolo_model_instance = YOLO(model_path)
        _loaded_model_path = model_path
        return _yolo_model_instance
    except Exception as e:
        raise ModelLoadError(
            f"Failed to load YOLO model weights from '{model_path}'. Error: {str(e)}"
        )


def reset_yolo_model_cache():
    """Resets the singleton instance cache (useful for tests or model path changes)."""
    global _yolo_model_instance, _loaded_model_path
    _yolo_model_instance = None
    _loaded_model_path = None
