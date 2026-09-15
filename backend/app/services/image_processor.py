import hashlib
import io
from typing import Tuple, List, Dict, Any
from PIL import Image as PILImage
import numpy as np
import cv2

from app.core.config import settings


class ImageValidationError(Exception):
    """Exception raised when image validation fails."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_file_header_and_size(file_bytes: bytes, filename: str, content_type: str) -> None:
    """Validates raw file size and basic constraints before processing."""
    if not file_bytes or len(file_bytes) == 0:
        raise ImageValidationError("Uploaded file is empty.", status_code=400)

    max_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ImageValidationError(
            f"File size exceeds maximum allowed limit of {settings.MAX_IMAGE_SIZE_MB}MB.",
            status_code=413
        )


def decode_and_validate_image(file_bytes: bytes) -> Tuple[PILImage.Image, str, int, int]:
    """Decodes image using PIL, validates image structure, format, and dimensions."""
    try:
        image = PILImage.open(io.BytesIO(file_bytes))
        image.verify()  # Verifies file integrity
    except Exception:
        raise ImageValidationError("File is corrupted or not a valid readable image.", status_code=400)

    # Re-open after verify() (verify invalidates image buffer for further processing)
    image = PILImage.open(io.BytesIO(file_bytes))

    pil_format = (image.format or "").upper()
    format_map = {
        "JPEG": "image/jpeg",
        "JPG": "image/jpeg",
        "PNG": "image/png",
        "WEBP": "image/webp"
    }

    detected_mime = format_map.get(pil_format)
    if not detected_mime or detected_mime not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise ImageValidationError(
            f"Unsupported image format ({pil_format or 'unknown'}). Supported formats: JPEG, PNG, WEBP.",
            status_code=415
        )

    width, height = image.size

    if width < settings.MIN_IMAGE_WIDTH or height < settings.MIN_IMAGE_HEIGHT:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) are below minimum required resolution ({settings.MIN_IMAGE_WIDTH}x{settings.MIN_IMAGE_HEIGHT}).",
            status_code=400
        )

    if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
        raise ImageValidationError(
            f"Image dimensions ({width}x{height}) exceed maximum allowed resolution ({settings.MAX_IMAGE_WIDTH}x{settings.MAX_IMAGE_HEIGHT}).",
            status_code=400
        )

    return image, detected_mime, width, height


def calculate_sha256(file_bytes: bytes) -> str:
    """Computes SHA-256 hash checksum of raw image bytes."""
    hasher = hashlib.sha256()
    hasher.update(file_bytes)
    return hasher.hexdigest()


def assess_image_quality(file_bytes: bytes) -> Tuple[int, List[str]]:
    """Performs deterministic image quality assessment (Brightness, Contrast, Blur/Sharpness).

    Returns:
        quality_score (0-100)
        quality_flags (List of warning strings)
    """
    flags = []
    score = 100

    try:
        # Convert bytes to numpy array for OpenCV analysis
        np_arr = np.frombuffer(file_bytes, np.uint8)
        img_cv = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img_cv is me or img_cv is None:
            return 80, ["UNABLE_TO_ANALYZE_QUALITY"]

        # Convert to Grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 1. Blur Detection (Laplacian Variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 50.0:
            score -= 30
            flags.append("BLURRY")

        # 2. Brightness Assessment (Mean Pixel Intensity)
        mean_brightness = float(np.mean(gray))
        if mean_brightness < 40:
            score -= 25
            flags.append("LOW_LIGHT")
        elif mean_brightness > 220:
            score -= 25
            flags.append("OVEREXPOSED")

        # 3. Contrast Assessment (Standard Deviation of Intensity)
        std_contrast = float(np.std(gray))
        if std_contrast < 20:
            score -= 20
            flags.append("LOW_CONTRAST")

    except Exception:
        # Fallback graceful assessment
        return 80, ["QUALITY_CHECK_SKIPPED"]

    score = max(0, min(100, score))
    return score, flags
