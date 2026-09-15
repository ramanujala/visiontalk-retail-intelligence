from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ImageResponse(BaseModel):
    id: UUID
    company_id: UUID
    store_id: UUID
    uploaded_by: UUID
    original_filename: str
    storage_key: str
    mime_type: str
    file_size: int
    width: int
    height: int
    checksum: str
    status: str
    quality_score: int
    quality_flags: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImageListResponse(BaseModel):
    items: List[ImageResponse]
    total: int
    page: int
    page_size: int
    pages: int
