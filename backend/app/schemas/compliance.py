from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ComplianceRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: str = Field(..., description="PRODUCT_REQUIRED, PRODUCT_QUANTITY, UNEXPECTED_PRODUCT, PRODUCT_ZONE, OCR_REQUIRED, CUSTOM_THRESHOLD")
    severity: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    configuration: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    store_id: Optional[UUID] = None


class ComplianceRuleCreate(ComplianceRuleBase):
    pass


class ComplianceRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rule_type: Optional[str] = None
    severity: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    store_id: Optional[UUID] = None


class ComplianceRuleResponse(ComplianceRuleBase):
    id: UUID
    company_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceFindingResponse(BaseModel):
    id: UUID
    company_id: UUID
    store_id: UUID
    image_id: UUID
    analysis_run_id: UUID
    rule_id: UUID
    status: str
    severity: str
    message: str
    details: Dict[str, Any] = {}
    evidence_references: List[dict] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplianceSummaryResponse(BaseModel):
    image_id: UUID
    analysis_run_id: UUID
    total_rules: int
    passed: int
    failed: int
    warnings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    findings: List[ComplianceFindingResponse] = []


class ComplianceAnalysisRunResponse(BaseModel):
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
    compliance_findings: List[ComplianceFindingResponse] = []

    model_config = ConfigDict(from_attributes=True)
