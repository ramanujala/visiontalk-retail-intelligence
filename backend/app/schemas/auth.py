from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class RegisterCompanyRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255, description="Full name of company tenant")
    company_slug: str = Field(..., min_length=2, max_length=255, description="Unique URL-friendly company identifier")
    admin_email: EmailStr = Field(..., description="Administrator email address")
    admin_password: str = Field(..., min_length=8, description="Administrator password (min 8 characters)")
    admin_full_name: str = Field(..., min_length=2, max_length=255, description="Administrator full name")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User login email")
    password: str = Field(..., description="User login password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    company: Optional[CompanyResponse] = None
