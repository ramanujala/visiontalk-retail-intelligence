from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.analysis import AnalysisRun, AnalysisType
from app.schemas.expected_actual import ExpectedActualAnalysisRunResponse
from app.api.deps import get_current_user
from app.services.expected_actual import ExpectedActualEngine
from app.services.evidence.exceptions import EvidenceNotFoundError

router = APIRouter(prefix="/analysis/expected-vs-actual", tags=["Expected vs Actual Analysis"])


@router.post("/{image_id}", response_model=ExpectedActualAnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def run_expected_vs_actual_analysis(
    image_id: UUID,
    force_reanalyze: bool = Query(False, description="Bypasses existing completed analysis check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes Expected vs Actual comparison analysis on an uploaded image with tenant isolation."""
    try:
        engine = ExpectedActualEngine(db)
        return engine.analyze(
            image_id=image_id,
            company_id=current_user.company_id,
            initiated_by_user_id=current_user.id,
            force_reanalyze=force_reanalyze
        )
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Expected vs Actual analysis failed: {str(exc)}"
        )


@router.get("/{analysis_id}", response_model=ExpectedActualAnalysisRunResponse)
def get_expected_vs_actual_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves an Expected vs Actual analysis run by ID enforcing tenant isolation."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.EXPECTED_VS_ACTUAL
    ).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expected vs Actual analysis run not found."
        )

    return run


@router.get("/image/{image_id}", response_model=List[ExpectedActualAnalysisRunResponse])
def list_expected_vs_actual_analyses_for_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all Expected vs Actual analyses performed for a specific image."""
    runs = db.query(AnalysisRun).filter(
        AnalysisRun.image_id == image_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.EXPECTED_VS_ACTUAL
    ).order_by(AnalysisRun.created_at.desc()).all()

    return runs
