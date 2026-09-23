"""Canonical Pydantic Schemas for Evidence Engine."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.services.detection.schemas import BoundingBox


class EvidenceDetectionItem(BaseModel):
    id: UUID
    analysis_run_id: UUID
    class_id: int
    class_name: str
    confidence: float
    bounding_box: BoundingBox
    related_ocr_ids: List[UUID] = []
    spatial_relationships: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class EvidenceOCRItem(BaseModel):
    id: UUID
    analysis_run_id: UUID
    text: str
    normalized_text: str
    confidence: float
    line_order: int
    bounding_box: BoundingBox

    model_config = ConfigDict(from_attributes=True)


class EvidenceMetadata(BaseModel):
    image_id: UUID
    company_id: UUID
    evidence_version: str = "1.0"
    total_detections: int
    total_ocr_regions: int
    total_associations: int
    detection_run_id: Optional[UUID] = None
    ocr_run_id: Optional[UUID] = None
    generated_at: datetime


class CanonicalEvidenceResponse(BaseModel):
    image_id: UUID
    company_id: UUID
    evidence_version: str = "1.0"
    metadata: EvidenceMetadata
    detections: List[EvidenceDetectionItem] = []
    ocr_results: List[EvidenceOCRItem] = []

    model_config = ConfigDict(from_attributes=True)
