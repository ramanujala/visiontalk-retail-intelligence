from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.analysis import AnalysisRun, AnalysisType
from app.models.compliance_rule import ComplianceFinding
from app.schemas.compliance import (
    ComplianceAnalysisRunResponse,
    ComplianceFindingResponse,
    ComplianceSummaryResponse
)
from app.api.deps import get_current_user
from app.services.compliance_engine import ComplianceEngine
from app.services.evidence.exceptions import EvidenceNotFoundError

router = APIRouter(prefix="/compliance", tags=["Compliance Engine"])


@router.post("/analyze/{image_id}", response_model=ComplianceAnalysisRunResponse, status_code=status.HTTP_201_CREATED)
def execute_compliance_analysis(
    image_id: UUID,
    force_reanalyze: bool = Query(False, description="Bypasses existing completed analysis check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Executes compliance rules evaluation on an image with tenant isolation."""
    try:
        engine = ComplianceEngine(db)
        return engine.evaluate_rules(
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
            detail=f"Compliance evaluation failed: {str(exc)}"
        )


@router.get("/image/{image_id}", response_model=List[ComplianceAnalysisRunResponse])
def list_compliance_analyses_for_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists compliance analyses executed for an image."""
    runs = db.query(AnalysisRun).filter(
        AnalysisRun.image_id == image_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.COMPLIANCE
    ).order_by(AnalysisRun.created_at.desc()).all()

    return runs


@router.get("/finding/{finding_id}", response_model=ComplianceFindingResponse)
def get_compliance_finding_detail(
    finding_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves a single compliance finding by ID enforcing tenant isolation."""
    finding = db.query(ComplianceFinding).filter(
        ComplianceFinding.id == finding_id,
        ComplianceFinding.company_id == current_user.company_id
    ).first()

    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance finding not found."
        )

    return finding


@router.get("/image/{image_id}/summary", response_model=ComplianceSummaryResponse)
def get_compliance_summary_for_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns compact summary metrics for an image's latest compliance analysis run."""
    run = db.query(AnalysisRun).filter(
        AnalysisRun.image_id == image_id,
        AnalysisRun.company_id == current_user.company_id,
        AnalysisRun.analysis_type == AnalysisType.COMPLIANCE
    ).order_by(AnalysisRun.created_at.desc()).first()

    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compliance analysis run not found."
        )

    findings: List[ComplianceFinding] = run.compliance_findings or []

    passed = sum(1 for f in findings if f.status == "PASS")
    failed = sum(1 for f in findings if f.status == "FAIL")
    warnings = sum(1 for f in findings if f.status == "WARNING")

    crit = sum(1 for f in findings if f.severity == "CRITICAL" and f.status != "PASS")
    high = sum(1 for f in findings if f.severity == "HIGH" and f.status != "PASS")
    med = sum(1 for f in findings if f.severity == "MEDIUM" and f.status != "PASS")
    low = sum(1 for f in findings if f.severity == "LOW" and f.status != "PASS")

    return ComplianceSummaryResponse(
        image_id=image_id,
        analysis_run_id=run.id,
        total_rules=len(findings),
        passed=passed,
        failed=failed,
        warnings=warnings,
        critical_findings=crit,
        high_findings=high,
        medium_findings=med,
        low_findings=low,
        findings=findings
    )
