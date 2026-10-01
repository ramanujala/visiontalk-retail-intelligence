from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LLMExplanationRequest(BaseModel):
    force_reanalyze: bool = Field(default=False, description="Force re-generation of explanation even if cached")
    question_context: Optional[str] = Field(default=None, description="Optional focus area or query for explanation")


class LLMExplanationResponse(BaseModel):
    analysis_run_id: str
    image_id: str
    status: str = Field(description="EXPLAINED, FALLBACK, or FAILED")
    explanation: str = Field(description="Grounded natural language explanation")
    key_findings: List[str] = Field(default_factory=list, description="Bullet point summary of key operational findings")
    evidence_references: Dict[str, Any] = Field(default_factory=dict, description="Traceability references to canonical detections, OCR, compliance")
    confidence: float = Field(description="Calculated visual evidence confidence score")
    fallback_reason: Optional[str] = Field(default=None, description="Reason if status is FALLBACK (e.g., LOW_CONFIDENCE, GEMINI_DISABLED, PROVIDER_ERROR)")
    model: str = Field(description="LLM model identifier used for explanation")
    created_at: datetime

    class Config:
        from_attributes = True
