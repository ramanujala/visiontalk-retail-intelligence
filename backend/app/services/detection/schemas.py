from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BoundingBox(BaseModel):
    x_min: float = Field(..., description="Min X coordinate (pixel or normalized)")
    y_min: float = Field(..., description="Min Y coordinate (pixel or normalized)")
    x_max: float = Field(..., description="Max X coordinate (pixel or normalized)")
    y_max: float = Field(..., description="Max Y coordinate (pixel or normalized)")


class DetectionResult(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: BoundingBox


class DetectionEvidence(BaseModel):
    image_width: int
    image_height: int
    total_detections: int
    detections: List[DetectionResult]
