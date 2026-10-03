from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetailResponse,
    MessageCreate,
    MessageResponse
)
from app.services.conversation_service import conversation_service

router = APIRouter(prefix="/conversations", tags=["Conversation System"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    body: Optional[ConversationCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new multi-turn conversation session for the authenticated user and company tenant.
    """
    req = body or ConversationCreate()
    return conversation_service.create_conversation(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        title=req.title
    )


@router.get("", response_model=List[ConversationResponse])
def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lists active conversation sessions for the authenticated user's tenant company.
    """
    return conversation_service.list_conversations_for_user(
        db=db,
        company_id=current_user.company_id,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a conversation session with chronologically ordered message history.
    Enforces strict tenant isolation.
    """
    return conversation_service.get_conversation_for_user(
        db=db,
        conversation_id=conversation_id,
        company_id=current_user.company_id,
        user_id=current_user.id
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Archives a conversation session.
    """
    conversation_service.archive_conversation(
        db=db,
        conversation_id=conversation_id,
        company_id=current_user.company_id,
        user_id=current_user.id
    )
    return None


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def post_message_to_conversation(
    conversation_id: str,
    body: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Posts a user message to a conversation.
    Routes the query via QuestionRouter, executes the capability, persists the Assistant response, and returns the message.
    """
    return conversation_service.post_user_message(
        db=db,
        conversation_id=conversation_id,
        company_id=current_user.company_id,
        user_id=current_user.id,
        content=body.content,
        image_id=body.image_id
    )
