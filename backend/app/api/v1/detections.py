import os
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, Detection, AnalysisRunStatus, AnalysisType
from app.schemas.analysis import AnalysisRunResponse, AnalysisRunSummaryResponse
from app.api.deps import get_current_user
from app.services.storage.local import LocalStorageProvider
from app.services.detection.detector import ObjectDetectionService
from app.services.detection.exceptions import InferenceError, ModelLoadError

router = APIRouter(prefix="/detections", tags=["Detections"])

storage_provider = LocalStorageProvider(base_dir=settings.STORAGE_DIR)
detection_service = ObjectDetectionService()


@router.post("/analyze/{image_id}", response_model=AnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def analyze_image_objects(
    image_id: UUID,
    force_reanalyze: bool = Query(False, description="If true, bypasses existing completed analysis check and runs fresh detection"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes YOLO object detection on an uploaded image with strict company tenant isolation."""
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
            AnalysisRun.analysis_type == AnalysisType.OBJECT_DETECTION,
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
        analysis_type=AnalysisType.OBJECT_DETECTION,
        status=AnalysisRunStatus.PENDING,
        model_name="YOLOv8",
        model_version=settings.YOLO_MODEL_PATH,
        started_at=datetime.now(timezone.utc)
    )
    db.add(analysis_run)
    db.commit()
    db.refresh(analysis_run)

    # 5. Run Synchronous YOLO Inference
    try:
        analysis_run.status = AnalysisRunStatus.RUNNING
        db.commit()

        evidence = detection_service.detect_objects(full_image_path)

        # 6. Persist Detections
        detection_objects = []
        for det in evidence.detections:
            detection_objects.append(
                Detection(
                    analysis_run_id=analysis_run.id,
                    company_id=current_user.company_id,
                    class_id=det.class_id,
                    class_name=det.class_name,
                    confidence=det.confidence,
                    x_min=det.bbox.x_min,
                    y_min=det.bbox.y_min,
                    x_max=det.bbox.x_max,
                    y_max=det.bbox.y_max
                )
            )

        if detection_objects:
            db.add_all(detection_objects)

        analysis_run.status = AnalysisRunStatus.COMPLETED
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run

    except (InferenceError, ModelLoadError) as model_err:
        db.rollback()
        analysis_run.status = AnalysisRunStatus.FAILED
        analysis_run.error_message = str(model_err)
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run
    except Exception as exc:
        db.rollback()
        analysis_run.status = AnalysisRunStatus.FAILED
        analysis_run.error_message = f"Unexpected processing error: {str(exc)}"
        analysis_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(analysis_run)
        return analysis_run


@router.get("/{analysis_run_id}", response_model=AnalysisRunResponse)
def get_analysis_run_detail(
    analysis_run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves an analysis run and its associated detections enforcing company tenant isolation."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_run_id,
        AnalysisRun.company_id == current_user.company_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis run not found."
        )

    return run


@router.get("/image/{image_id}", response_model=List[AnalysisRunResponse])
def list_analysis_runs_for_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all object detection analysis runs performed for a specific image in the tenant."""
    # First verify image exists in tenant
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
        AnalysisRun.company_id == current_user.company_id
    ).order_by(AnalysisRun.created_at.desc()).all()

    return runs


@router.get("/{analysis_run_id}/summary", response_model=AnalysisRunSummaryResponse)
def get_analysis_run_summary(
    analysis_run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns compact summary metrics for an object detection run."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_run_id,
        AnalysisRun.company_id == current_user.company_id
    ).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis run not found."
        )

    detections = run.detections or []
    detected_classes = sorted(list(set(d.class_name for d in detections)))
    confidences = [d.confidence for d in detections]

    conf_stats = {
        "min": min(confidences) if confidences else 0.0,
        "max": max(confidences) if confidences else 0.0,
        "avg": round(sum(confidences) / len(confidences), 4) if confidences else 0.0
    }

    return AnalysisRunSummaryResponse(
        analysis_run_id=run.id,
        image_id=run.image_id,
        status=run.status,
        total_detections=len(detections),
        detected_classes=detected_classes,
        confidence_stats=conf_stats,
        model_info={
            "model_name": run.model_name,
            "model_version": run.model_version
        }
    )
