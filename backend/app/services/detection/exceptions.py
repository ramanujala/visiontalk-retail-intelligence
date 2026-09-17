class ModelLoadError(Exception):
    """Exception raised when YOLO model weights cannot be loaded."""
    pass

class InferenceError(Exception):
    """Exception raised when object detection inference fails."""
    pass
