import os
import re
from typing import List
from PIL import Image as PILImage

from app.core.config import settings
from app.services.detection.schemas import BoundingBox
from app.services.ocr.model import get_paddle_ocr_engine
from app.services.ocr.schemas import OCREvidence, OCRResultItem
from app.services.ocr.exceptions import OCRInferenceError


def normalize_ocr_text(raw_text: str) -> str:
    """Safe, deterministic whitespace normalization preserving character content."""
    if not raw_text:
        return ""
    # Strip leading/trailing spaces and collapse repeated whitespace
    return re.sub(r'\s+', ' ', raw_text.strip())


class OCRService:
    """Service handling PaddleOCR inference and normalizing outputs into structured text evidence."""

    def __init__(self, confidence_threshold: float = None):
        self.conf_thresh = confidence_threshold if confidence_threshold is not None else settings.OCR_CONFIDENCE_THRESHOLD

    def extract_text(self, image_path: str) -> OCREvidence:
        """Executes OCR text extraction on the given image path and returns structured evidence."""
        if not os.path.exists(image_path):
            raise OCRInferenceError(f"Image file does not exist at path: {image_path}")

        # Get original image dimensions
        try:
            with PILImage.open(image_path) as img:
                img_width, img_height = img.size
        except Exception as img_err:
            raise OCRInferenceError(f"Failed to read image dimensions: {str(img_err)}")

        # Run PaddleOCR inference
        try:
            engine = get_paddle_ocr_engine()
            results = engine.ocr(image_path, cls=settings.OCR_USE_ANGLE_CLS)
        except Exception as err:
            raise OCRInferenceError(f"PaddleOCR execution failed: {str(err)}")

        regions: List[OCRResultItem] = []

        if results and len(results) > 0 and results[0] is not None:
            line_counter = 1
            for res in results[0]:
                if not res or len(res) < 2:
                    continue
                
                bbox_points = res[0]  # Points: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                text_info = res[1]    # (text, confidence)

                if not text_info or len(text_info) < 2:
                    continue

                raw_text = str(text_info[0])
                confidence = float(text_info[1])

                # Confidence threshold filtering
                if confidence < self.conf_thresh:
                    continue

                normalized_text = normalize_ocr_text(raw_text)
                if not normalized_text:
                    continue

                # Calculate bounding box envelope from 4 points
                xs = [pt[0] for pt in bbox_points]
                ys = [pt[1] for pt in bbox_points]

                x_min = round(float(min(xs)), 2)
                y_min = round(float(min(ys)), 2)
                x_max = round(float(max(xs)), 2)
                y_max = round(float(max(ys)), 2)

                regions.append(
                    OCRResultItem(
                        text=raw_text,
                        normalized_text=normalized_text,
                        confidence=round(confidence, 4),
                        line_order=line_counter,
                        bbox=BoundingBox(
                            x_min=x_min,
                            y_min=y_min,
                            x_max=x_max,
                            y_max=y_max
                        )
                    )
                )
                line_counter += 1

        return OCREvidence(
            image_width=img_width,
            image_height=img_height,
            total_regions=len(regions),
            regions=regions
        )
