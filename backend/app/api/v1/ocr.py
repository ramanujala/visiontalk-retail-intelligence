import os
from datetime import datetime, timezone
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, OCRResult, AnalysisRunStatus, AnalysisType
from app.schemas.ocr import OCRAnalysisRunResponse, OCRSummaryResponse
from app.api.deps import get_current_user
from app.services.storage.local import LocalStorageProvider
from app.services.ocr.ocr import OCRService
from app.services.ocr.exceptions import OCRInferenceError, OCRDependencyError

router = APIRouter(prefix="/ocr", tags=["OCR"])

storage_provider = LocalStorageProvider(base_dir=settings.STORAGE_DIR)
ocr_service = OCRService()


@router.post("/analyze/{image_id}", response_model=OCRAnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def analyze_image_text(
    image_id: UUID,
    force_reanalyze: bool = Query(False, description="If true, bypasses existing completed OCR analysis check and runs fresh extraction"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes OCR text extraction on an uploaded image with strict company tenant isolation."""
    # 1. Validate Image Ownership and Status
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.company_id == current_user.company_id,
        Image.status != ImageStatus.DELETED
    ).first()

    if not image:
        # Return 404 to avoid leaking cross-tenant image existence
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found."
        )

    # 2. Check for Existing Completed Analysis (Duplicate Analysis Prevention Strategy)
    if not force_reanalyze:
        existing_run = db.query(AnalysisRun).filter(
            AnalysisRun.image_id == image_id,
            AnalysisRun.company_id == current_user.company_id,
            AnalysisRun.analysis_type == AnalysisType.OCR,
            AnalysisRun.status == AnalysisRunStatus.COMPLETED
        ).order_by(AnalysisRun.created_at.desc()).first()

        if existing_run:
            return existing_run

    # 3. Resolve Stored Physical File Path
    full_image_path = os.path.join(storage_provider.base_dir, image.storage_key)
    if not os.path.exists(full_image_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stored image file is missing or inaccessible on server storage."
        )

    # 4. Create AnalysisRun in PENDING state
    analysis_run = AnalysisRun(
        company_id=current_user.company_id,
        image_id=image_id,
        initiated_by=current_user.id,
        analysis_type=AnalysisType.OCR,
        status=AnalysisRunStatus.PENDING,
        model_name="PaddleOCR",
        model_version=f"paddleocr-{settings.OCR_LANGUAGE}",
        started_at=datetime.now(timezone.utc)
    )
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)

    # 5. Run Synchronous PaddleOCR Text Extraction
    try:
        analysis_run.status = AnalysisRunStatus.RUNNING
        db.commit()

        evidence = ocr_service.extract_text(full_image_path)

        # 6. Persist OCR Results
        ocr_objects = []
        for reg in evidence.regions:
            ocr_objects.append(
                OCRResult(
                    analysis_run_id=analysis_run.id,
                    company_id=current_user.company_id,
                    text=reg.text,
                    normalized_text=reg.normalized_text,
                    confidence=reg.confidence,
                    line_order=reg.line_order,
                    x_min=reg.bbox.x_min,
                    y_min=reg.bbox.y_min,
                    x_max=reg.bbox.x_max,
                    y_max=reg.bbox.y_max
                )
            )

        if ocr_objects:
            db.add_all(ocr_objects)

        analysis_run.status = AnalysisRunStatus.COMPLETED
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run

    except (OCRInferenceError, OCRDependencyError) as ocr_err:
        db.rollback()
        analysis_run.status = AnalysisRunStatus.FAILED
        analysis_run.error_message = str(ocr_err)
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run
    except Exception as exc:
        db.rollback()
        analysis_run.status = AnalysisRunStatus.FAILED
        analysis_run.error_message = f"Unexpected OCR processing error: {str(exc)}"
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run


@router.get("/{analysis_run_id}", response_model=OCRAnalysisRunResponse)
def get_ocr_analysis_run_detail(
    analysis_run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves an OCR analysis run and its associated recognized text items enforcing company tenant isolation."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_run_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.OCR
    ).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR Analysis run not found."
        )

    return run


@router.get("/image/{image_id}", response_model=List[OCRAnalysisRunResponse])
def list_ocr_analysis_runs_for_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all OCR analysis runs performed for a specific image in the tenant."""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.company_id == current_user.company_id,
        Image.status != ImageStatus.DELETED
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found."
        )

    runs = db.query(AnalysisRun).filter(
        AnalysisRun.image_id == image_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.OCR
    ).order_by(AnalysisRun.created_at.desc()).all()

    return runs


@router.get("/{analysis_run_id}/summary", response_model=OCRSummaryResponse)
def get_ocr_analysis_run_summary(
    analysis_run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns compact summary metrics for an OCR text extraction run."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_run_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.OCR
    ).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OCR Analysis run not found."
        )

    results = run.ocr_results or []
    confidences = [r.confidence for r in results]
    sample_texts = [r.normalized_text for r in results[:10]]

    conf_stats = {
        "min": min(confidences) if confidences else 0.0,
        "max": max(confidences) if confidences else 0.0,
        "avg": round(sum(confidences) / len(confidences), 4) if confidences else 0.0
    }

    return OCRSummaryResponse(
        analysis_run_id=run.id,
        image_id=run.image_id,
        status=run.status,
        total_regions=len(results),
        confidence_stats=conf_stats,
        extracted_text_sample=sample_texts,
        model_info={
            "model_name": run.model_name,
            "model_version": run.model_version
        }
    )
