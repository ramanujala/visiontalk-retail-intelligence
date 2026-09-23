from typing import Optional
from app.core.config import settings
from app.services.ocr.exceptions import OCRDependencyError

# Lazy singleton model reference
_paddle_ocr_instance = None
_loaded_lang: Optional[str] = None


def get_paddle_ocr_engine():
    """Lazy loads and caches the PaddleOCR singleton engine instance."""
    global _paddle_ocr_instance, _loaded_lang

    if not settings.OCR_ENABLED:
        raise OCRDependencyError("OCR service is currently disabled in configuration.")

    lang = settings.OCR_LANGUAGE

    if _paddle_ocr_instance is not None and _loaded_lang == lang:
        return _paddle_ocr_instance

    try:
        from paddleocr import PaddleOCR
        # Initialize PaddleOCR engine with configured options
        _paddle_ocr_instance = PaddleOCR(
            use_angle_cls=settings.OCR_USE_ANGLE_CLS,
            lang=lang,
            show_log=False
        )
        _loaded_lang = lang
        return _paddle_ocr_instance
    except Exception as e:
        raise OCRDependencyError(
            f"Failed to initialize PaddleOCR engine (lang='{lang}'). Ensure PaddleOCR dependencies are installed. Error: {str(e)}"
        )


def reset_paddle_ocr_cache():
    """Resets the singleton engine cache (useful for unit testing)."""
    global _paddle_ocr_instance, _loaded_lang
    _paddle_ocr_instance = None
    _loaded_lang = None
