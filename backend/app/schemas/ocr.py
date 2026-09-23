from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.services.detection.schemas import BoundingBox


class OCRResultResponseItem(BaseModel):
    id: UUID
    analysis_run_id: UUID
    company_id: UUID
    text: str
    normalized_text: str
    confidence: float
    line_order: int
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OCRAnalysisRunResponse(BaseModel):
    id: UUID
    company_id: UUID
    image_id: UUID
    initiated_by: UUID
    analysis_type: str
    status: str
    model_name: str
    model_version: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    ocr_results: List[OCRResultResponseItem] = []

    model_config = ConfigDict(from_attributes=True)


class OCRSummaryResponse(BaseModel):
    analysis_run_id: UUID
    image_id: UUID
    status: str
    total_regions: int
    confidence_stats: dict
    extracted_text_sample: List[str]
    model_info: dict
