from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.image import Image
from app.models.analysis import AnalysisRun, AnalysisRunStatus, AnalysisType
from app.schemas.llm_explanation import LLMExplanationRequest, LLMExplanationResponse
from app.services.llm_service import llm_service
from app.services.evidence.engine import EvidenceEngine
from app.services.expected_actual import ExpectedActualEngine
from app.services.compliance_engine import ComplianceEngine

router = APIRouter(prefix="/llm", tags=["Gemini / Vision LLM Explanation"])


@router.post("/explain/{image_id}", response_model=LLMExplanationResponse)
def generate_image_explanation(
    image_id: str,
    body: Optional[LLMExplanationRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate grounded natural-language explanation of retail shelf image.
    Uses Phase 4-8 deterministic results as authoritative evidence input for Gemini.
    """
    req_body = body or LLMExplanationRequest()

    # 1. Validate image ownership & tenant isolation
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.company_id == current_user.company_id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found or access denied."
        )

    # 2. Check for completed existing explanation run unless force_reanalyze is True
    if not req_body.force_reanalyze:
        existing_run = db.query(AnalysisRun).filter(
            AnalysisRun.image_id == image.id,
            AnalysisRun.company_id == current_user.company_id,
            AnalysisRun.analysis_type == AnalysisType.LLM_EXPLANATION,
            AnalysisRun.status == AnalysisRunStatus.COMPLETED
        ).order_by(AnalysisRun.completed_at.desc()).first()

        if existing_run and existing_run.error_message:
            try:
                import json
                cached_payload = json.loads(existing_run.error_message)
                return LLMExplanationResponse(**cached_payload)
            except Exception:
                pass

    # 3. Gather deterministic evidence from earlier phases
    try:
        ev_engine = EvidenceEngine(db)
        evidence = ev_engine.generate_canonical_evidence(image.id, current_user.company_id).model_dump(mode="json")
    except Exception:
        evidence = {"detections": [], "ocr_results": []}

    try:
        ea_engine = ExpectedActualEngine(db)
        expected_actual_res = ea_engine.analyze(image.id, current_user.company_id, current_user.id, force_reanalyze=False)
        expected_actual = expected_actual_res.model_dump(mode="json")
    except Exception:
        expected_actual = None

    try:
        comp_engine = ComplianceEngine(db)
        comp_summary = comp_engine.get_compliance_summary(image.id, current_user.company_id).model_dump(mode="json")
        compliance = comp_summary
    except Exception:
        compliance = None

    # 4. Generate LLM Explanation
    result = llm_service.generate_explanation(
        image=image,
        evidence_data=evidence,
        expected_actual_data=expected_actual,
        compliance_data=compliance,
        question_context=req_body.question_context
    )

    # 5. Persist AnalysisRun record
    analysis_run = AnalysisRun(
        company_id=current_user.company_id,
        image_id=image.id,
        initiated_by=current_user.id,
        analysis_type=AnalysisType.LLM_EXPLANATION,
        status=AnalysisRunStatus.COMPLETED,
        model_name=llm_service.model_name,
        model_version="1.0",
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
    )

    # Store formatted JSON response string in error_message column for lightweight caching
    import json
    response_payload = {
        "analysis_run_id": str(analysis_run.id),
        "image_id": str(image.id),
        "status": result["status"],
        "explanation": result["explanation"],
        "key_findings": result["key_findings"],
        "evidence_references": result["evidence_references"],
        "confidence": result["confidence"],
        "fallback_reason": result["fallback_reason"],
        "model": result["model"],
        "created_at": result["created_at"].isoformat()
    }
    analysis_run.error_message = json.dumps(response_payload)

    db.add(analysis_run)
    db.commit()

    return LLMExplanationResponse(**response_payload)


@router.get("/explanation/{analysis_run_id}", response_model=LLMExplanationResponse)
def get_explanation_run(
    analysis_run_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve stored LLM explanation analysis run by ID.
    """
    run = db.query(AnalysisRun).filter(
        AnalysisRun.id == analysis_run_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.LLM_EXPLANATION
    ).first()

    if not run or not run.error_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM Explanation analysis run not found or access denied."
        )

    import json
    payload = json.loads(run.error_message)
    return LLMExplanationResponse(**payload)
