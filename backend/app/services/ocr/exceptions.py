class OCRDependencyError(Exception):
    """Exception raised when PaddleOCR dependency or model weights cannot be loaded."""
    pass

class OCRInferenceError(Exception):
    """Exception raised when OCR text extraction inference fails."""
    pass
