from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.services.detection.schemas import BoundingBox


class OCRResultItem(BaseModel):
    text: str
    normalized_text: str
    confidence: float
    line_order: int
    bbox: BoundingBox


class OCREvidence(BaseModel):
    image_width: int
    image_height: int
    total_regions: int
    regions: List[OCRResultItem]
