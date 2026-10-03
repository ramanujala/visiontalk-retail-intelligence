from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.image import Image
from app.schemas.question_router import QuestionRouteRequest, QuestionRouteResult
from app.services.question_router import question_router

router = APIRouter(prefix="/questions", tags=["Question Router"])


@router.post("/route", response_model=QuestionRouteResult, status_code=status.HTTP_200_OK)
def route_user_question(
    request: QuestionRouteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Evaluates a user question and determines which analysis capability (Detection, Expected vs Actual, Compliance, or LLM) should process it.
    Validates tenant image access if image_id is provided.
    """
    if request.image_id:
        # Enforce tenant isolation if image_id is provided
        image = db.query(Image).filter(
            Image.id == request.image_id,
            Image.company_id == current_user.company_id
        ).first()

        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found or access denied."
            )

    return question_router.route_question(request)
