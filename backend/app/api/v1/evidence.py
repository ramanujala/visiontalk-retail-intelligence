"""Evidence Engine API endpoints (/api/v1/evidence)."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.schemas.evidence import CanonicalEvidenceResponse
from app.api.deps import get_current_user
from app.services.evidence.engine import EvidenceEngine
from app.services.evidence.exceptions import EvidenceNotFoundError, EvidenceGenerationError

router = APIRouter(prefix="/evidence", tags=["Evidence Engine"])


@router.post("/generate/{image_id}", response_model=CanonicalEvidenceResponse, status_code=status.HTTP_200_OK)
def generate_canonical_evidence_for_image(
    image_id: UUID,
    overlap_threshold: float = Query(0.1, ge=0.0, le=1.0, description="Minimum overlap ratio for OCR-detection association"),
    max_center_distance: float = Query(500.0, ge=0.0, description="Maximum center distance for spatial association"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generates canonical evidence combining detection and OCR outputs for an image with tenant isolation."""
    try:
        engine = EvidenceEngine(db)
        return engine.generate_canonical_evidence(
            image_id=image_id,
            company_id=current_user.company_id,
            overlap_threshold=overlap_threshold,
            max_center_distance=max_center_distance
        )
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate canonical evidence: {str(exc)}"
        )


@router.get("/image/{image_id}", response_model=CanonicalEvidenceResponse)
def get_canonical_evidence_for_image(
    image_id: UUID,
    overlap_threshold: float = Query(0.1, ge=0.0, le=1.0),
    max_center_distance: float = Query(500.0, ge=0.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves the current canonical evidence aggregation for a tenant's image."""
    try:
        engine = EvidenceEngine(db)
        return engine.generate_canonical_evidence(
            image_id=image_id,
            company_id=current_user.company_id,
            overlap_threshold=overlap_threshold,
            max_center_distance=max_center_distance
        )
    except EvidenceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve canonical evidence: {str(exc)}"
        )
