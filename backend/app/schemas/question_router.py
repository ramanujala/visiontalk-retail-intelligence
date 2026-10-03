from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class QuestionIntent(str, Enum):
    COUNT = "COUNT"
    AVAILABILITY = "AVAILABILITY"
    EXPECTED_VS_ACTUAL = "EXPECTED_VS_ACTUAL"
    COMPLIANCE = "COMPLIANCE"
    GENERAL = "GENERAL"
    UNKNOWN = "UNKNOWN"


class QuestionRouteRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User retail audit question")
    image_id: Optional[str] = Field(default=None, description="Optional image ID for contextual tenant validation")


class QuestionRouteResult(BaseModel):
    question: str
    intent: QuestionIntent
    route: str = Field(description="Target capability service route handler")
    confidence: float = Field(description="Intent classification confidence (0.0 to 1.0)")
    reason: str = Field(description="Explanation of classification rule or strategy")
    target_service: str = Field(description="Internal service capability identifier")
