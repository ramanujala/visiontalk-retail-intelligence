import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.conversation import Conversation, Message, MessageRole
from app.models.image import Image
from app.schemas.question_router import QuestionRouteRequest
from app.services.question_router import question_router
from app.services.route_executor import RouteExecutor

logger = logging.getLogger(__name__)


class ConversationService:
    """
    Core domain service managing multi-turn conversation sessions, message history,
    QuestionRouter orchestration, and execution via RouteExecutor.
    Enforces strict tenant isolation and owner access control.
    """

    def create_conversation(
        self, db: Session, company_id: Any, user_id: Any, title: Optional[str] = "Retail Audit Chat"
    ) -> Conversation:
        conversation = Conversation(
            company_id=company_id,
            user_id=user_id,
            title=title or "Retail Audit Chat"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_conversation_for_user(
        self, db: Session, conversation_id: str, company_id: Any, user_id: Any
    ) -> Conversation:
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.company_id == company_id
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found or access denied."
            )
        return conversation

    def list_conversations_for_user(
        self, db: Session, company_id: Any, user_id: Any, skip: int = 0, limit: int = 50
    ) -> List[Conversation]:
        return db.query(Conversation).filter(
            Conversation.company_id == company_id,
            Conversation.is_archived == False
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def archive_conversation(
        self, db: Session, conversation_id: str, company_id: Any, user_id: Any
    ) -> bool:
        conversation = self.get_conversation_for_user(db, conversation_id, company_id, user_id)
        conversation.is_archived = True
        db.commit()
        return True

    def post_user_message(
        self,
        db: Session,
        conversation_id: str,
        company_id: Any,
        user_id: Any,
        content: str,
        image_id: Optional[str] = None
    ) -> Message:
        # 1. Validate conversation ownership & tenant isolation
        conversation = self.get_conversation_for_user(db, conversation_id, company_id, user_id)

        # 2. Validate image tenant isolation if provided
        image = None
        if image_id:
            image = db.query(Image).filter(
                Image.id == image_id,
                Image.company_id == company_id
            ).first()
            if not image:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Specified image not found or access denied."
                )

        # 3. Save User Message
        user_msg = Message(
            conversation_id=conversation.id,
            image_id=image.id if image else None,
            role=MessageRole.USER,
            content=content,
            msg_metadata={}
        )
        db.add(user_msg)
        db.flush()

        # 4. Route User Question via QuestionRouter
        route_req = QuestionRouteRequest(question=content, image_id=str(image.id) if image else None)
        route_result = question_router.route_question(route_req)

        # 5. Execute Route via RouteExecutor
        executor = RouteExecutor(db)
        execution_res = executor.execute_route(
            route_result=route_result,
            image=image,
            company_id=company_id,
            user_id=user_id,
            user_question=content
        )

        # 6. Save Assistant Response Message
        assistant_msg = Message(
            conversation_id=conversation.id,
            image_id=image.id if image else None,
            role=MessageRole.ASSISTANT,
            content=execution_res.get("answer", "No response generated."),
            intent=route_result.intent.value,
            route=route_result.route,
            msg_metadata=execution_res.get("metadata", {})
        )
        db.add(assistant_msg)

        # 7. Update conversation timestamp
        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(assistant_msg)

        return assistant_msg


conversation_service = ConversationService()
