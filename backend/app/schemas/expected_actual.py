from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ExpectedProductBase(BaseModel):
    product_name: str = Field(..., min_length=1, max_length=255)
    product_code: str = Field(..., min_length=1, max_length=100)
    expected_quantity: int = Field(1, ge=0)
    expected_min_quantity: int = Field(1, ge=0)
    expected_max_quantity: int = Field(10, ge=0)
    is_active: bool = True

    @field_validator("product_code")
    @classmethod
    def normalize_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("product_name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        return v.strip()


class ExpectedProductCreate(ExpectedProductBase):
    store_id: UUID

    @field_validator("expected_max_quantity")
    @classmethod
    def validate_quantities(cls, max_qty: int, info: Any) -> int:
        min_qty = info.data.get("expected_min_quantity", 0)
        if max_qty < min_qty:
            raise ValueError("expected_max_quantity cannot be less than expected_min_quantity")
        return max_qty


class ExpectedProductUpdate(BaseModel):
    product_name: Optional[str] = Field(None, min_length=1, max_length=255)
    product_code: Optional[str] = Field(None, min_length=1, max_length=100)
    expected_quantity: Optional[int] = Field(None, ge=0)
    expected_min_quantity: Optional[int] = Field(None, ge=0)
    expected_max_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @field_validator("product_code")
    @classmethod
    def normalize_code(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().upper() if v else v


class ExpectedProductResponse(ExpectedProductBase):
    id: UUID
    company_id: UUID
    store_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpectedActualItemResponse(BaseModel):
    id: UUID
    analysis_run_id: UUID
    company_id: UUID
    expected_product_id: Optional[UUID] = None
    product_code: str
    product_name: str
    expected_quantity: int
    expected_min_quantity: int
    expected_max_quantity: int
    observed_quantity: int
    difference: int
    status: str
    evidence_references: List[dict] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpectedActualIssueResponse(BaseModel):
    id: UUID
    analysis_run_id: UUID
    company_id: UUID
    store_id: UUID
    image_id: UUID
    expected_product_id: Optional[UUID] = None
    issue_type: str
    severity: str
    message: str
    evidence_references: List[dict] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExpectedActualAnalysisRunResponse(BaseModel):
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
    expected_actual_items: List[ExpectedActualItemResponse] = []
    expected_actual_issues: List[ExpectedActualIssueResponse] = []

    model_config = ConfigDict(from_attributes=True)
