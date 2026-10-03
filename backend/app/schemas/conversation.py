from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="Retail Audit Chat", description="Optional title for the conversation session")


class ConversationResponse(BaseModel):
    id: UUID
    company_id: UUID
    user_id: UUID
    title: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Message text content")
    image_id: Optional[UUID] = Field(default=None, description="Optional image ID reference for analysis context")


class MessageResponse(BaseModel):
    id: UUID
    conversation_id: UUID
    image_id: Optional[UUID] = None
    role: str
    content: str
    intent: Optional[str] = None
    route: Optional[str] = None
    msg_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationDetailResponse(ConversationResponse):
    messages: List[MessageResponse] = Field(default_factory=list)
