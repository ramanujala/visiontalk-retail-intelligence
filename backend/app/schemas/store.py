from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class StoreCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Store name")
    code: str = Field(..., min_length=1, max_length=50, description="Unique store code within company")
    location: Optional[str] = Field(None, max_length=255, description="Store address or physical location")


class StoreUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None


class StoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    name: str
    code: str
    location: Optional[str] = None
    is_active: bool
    created_at: datetime
