"""Expected vs Actual Reasoning Engine Service Layer.

Consumes canonical Evidence from EvidenceEngine (Phase 6) and configured ExpectedProducts to:
- Deterministically match observed detection/OCR evidence against active expectations
- Evaluate quantities (OBSERVED, MISSING, LOW_STOCK, EXCESS, UNEXPECTED, UNMATCHED)
- Generate explainable issues with evidence references
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Set
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.image import Image, ImageStatus
from app.models.store import Store
from app.models.expected_product import ExpectedProduct
from app.models.analysis import (
    AnalysisRun,
    AnalysisRunStatus,
    AnalysisType,
    ExpectedActualItem,
    ExpectedActualIssue,
    ExpectedActualItemStatus,
    ExpectedActualIssueType,
    ExpectedActualIssueSeverity
)
from app.services.evidence.engine import EvidenceEngine
from app.services.evidence.exceptions import EvidenceNotFoundError
from app.schemas.evidence import CanonicalEvidenceResponse, EvidenceDetectionItem, EvidenceOCRItem


class ExpectedActualEngine:
    def __init__(self, db: Session):
        self.db = db

    def analyze(
        self,
        image_id: UUID,
        company_id: UUID,
        initiated_by_user_id: UUID,
        force_reanalyze: bool = False
    ) -> AnalysisRun:
        """Executes Expected vs Actual comparison analysis on an image."""
        # 1. Validate Image & Tenant Isolation
        image = self.db.query(Image).filter(
            Image.id == image_id,
            Image.company_id == company_id,
            Image.status != ImageStatus.DELETED
        ).first()

        if not image:
            raise EvidenceNotFoundError("Image not found.")

        # 2. Check existing completed AnalysisRun if force_reanalyze is False
        if not force_reanalyze:
            existing_run = self.db.query(AnalysisRun).filter(
                AnalysisRun.image_id == image_id,
                AnalysisRun.company_id == company_id,
                AnalysisRun.analysis_type == AnalysisType.EXPECTED_VS_ACTUAL,
                AnalysisRun.status == AnalysisRunStatus.COMPLETED
            ).order_by(AnalysisRun.created_at.desc()).first()

            if existing_run:
                return existing_run

        # 3. Obtain Canonical Evidence from Phase 6 EvidenceEngine
        evidence_engine = EvidenceEngine(self.db)
        canonical_evidence = evidence_engine.generate_canonical_evidence(
            image_id=image_id,
            company_id=company_id
        )

        # 4. Fetch Active Store Expectations for Image's Store
        active_expectations: List[ExpectedProduct] = self.db.query(ExpectedProduct).filter(
            ExpectedProduct.company_id == company_id,
            ExpectedProduct.store_id == image.store_id,
            ExpectedProduct.is_active == True
        ).all()

        # 5. Create AnalysisRun record in PENDING state
        analysis_run = AnalysisRun(
            company_id=company_id,
            image_id=image_id,
            initiated_by=initiated_by_user_id,
            analysis_type=AnalysisType.EXPECTED_VS_ACTUAL,
            status=AnalysisRunStatus.RUNNING,
            model_name="ExpectedActualEngine",
            model_version="1.0",
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(analysis_run)
        self.db.commit()
        self.db.refresh(analysis_run)

        try:
            # 6. Execute Deterministic Evidence Matching & Quantity Logic
            items_to_create, issues_to_create = self._process_comparison(
                analysis_run_id=analysis_run.id,
                company_id=company_id,
                store_id=image.store_id,
                image_id=image_id,
                expectations=active_expectations,
                evidence=canonical_evidence
            )

            if items_to_create:
                self.db.add_all(items_to_create)
            if issues_to_create:
                self.db.add_all(issues_to_create)

            analysis_run.status = AnalysisRunStatus.COMPLETED
            analysis_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(analysis_run)
            return analysis_run

        except Exception as exc:
            self.db.rollback()
            analysis_run.status = AnalysisRunStatus.FAILED
            analysis_run.error_message = f"Expected vs Actual analysis failed: {str(exc)}"
            analysis_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(analysis_run)
            return analysis_run

    def _process_comparison(
        self,
        analysis_run_id: UUID,
        company_id: UUID,
        store_id: UUID,
        image_id: UUID,
        expectations: List[ExpectedProduct],
        evidence: CanonicalEvidenceResponse
    ) -> Tuple[List[ExpectedActualItem], List[ExpectedActualIssue]]:
        """Core deterministic matching and evaluation logic."""

        # Index expectations by normalized product_code & normalized product_name
        exp_by_code: Dict[str, ExpectedProduct] = {exp.product_code.upper(): exp for exp in expectations}
        exp_by_name: Dict[str, ExpectedProduct] = {exp.product_name.lower(): exp for exp in expectations}

        # Track matching observations to expectations
        # exp_id -> list of matched detection evidence dicts
        matched_obs_per_exp: Dict[UUID, List[dict]] = {exp.id: [] for exp in expectations}

        unmatched_detections: List[EvidenceDetectionItem] = []
        unmatched_ocr_results: List[EvidenceOCRItem] = []

        # Process Object Detections & associated OCR text
        for det in evidence.detections:
            det_class_norm = det.class_name.strip()
            det_class_upper = det_class_norm.upper()
            det_class_lower = det_class_norm.lower()

            # Find matching expectation by code or name
            matched_exp: Optional[ExpectedProduct] = exp_by_code.get(det_class_upper) or exp_by_name.get(det_class_lower)

            # Check if associated OCR text contains an expectation code/name
            if not matched_exp and det.spatial_relationships:
                for rel in det.spatial_relationships:
                    ocr_text_upper = rel["ocr_text"].strip().upper()
                    ocr_text_lower = rel["ocr_text"].strip().lower()
                    if ocr_text_upper in exp_by_code:
                        matched_exp = exp_by_code[ocr_text_upper]
                        break
                    elif ocr_text_lower in exp_by_name:
                        matched_exp = exp_by_name[ocr_text_lower]
                        break

            evidence_ref = {
                "detection_id": str(det.id),
                "class_name": det.class_name,
                "confidence": det.confidence,
                "bounding_box": det.bounding_box.model_dump(),
                "related_ocr": det.spatial_relationships
            }

            if matched_exp:
                matched_obs_per_exp[matched_exp.id].append(evidence_ref)
            else:
                unmatched_detections.append(det)

        # Generate Expected vs Actual Items & Issues for Configured Expectations
        items: List[ExpectedActualItem] = []
        issues: List[ExpectedActualIssue] = []

        for exp in expectations:
            obs_refs = matched_obs_per_exp[exp.id]
            obs_qty = len(obs_refs)
            diff = obs_qty - exp.expected_quantity

            item_status: str
            if obs_qty == 0:
                item_status = ExpectedActualItemStatus.MISSING
                issues.append(
                    ExpectedActualIssue(
                        analysis_run_id=analysis_run_id,
                        company_id=company_id,
                        store_id=store_id,
                        image_id=image_id,
                        expected_product_id=exp.id,
                        issue_type=ExpectedActualIssueType.MISSING_PRODUCT,
                        severity=ExpectedActualIssueSeverity.HIGH,
                        message=f"Expected product '{exp.product_name}' (Code: {exp.product_code}) was not observed on shelf (Expected: {exp.expected_quantity}).",
                        evidence_references=[]
                    )
                )
            elif obs_qty < exp.expected_min_quantity:
                item_status = ExpectedActualItemStatus.LOW_STOCK
                issues.append(
                    ExpectedActualIssue(
                        analysis_run_id=analysis_run_id,
                        company_id=company_id,
                        store_id=store_id,
                        image_id=image_id,
                        expected_product_id=exp.id,
                        issue_type=ExpectedActualIssueType.LOW_STOCK,
                        severity=ExpectedActualIssueSeverity.MEDIUM,
                        message=f"Expected product '{exp.product_name}' is low stock (Observed: {obs_qty}, Min Required: {exp.expected_min_quantity}).",
                        evidence_references=obs_refs
                    )
                )
            elif obs_qty > exp.expected_max_quantity:
                item_status = ExpectedActualItemStatus.EXCESS
                issues.append(
                    ExpectedActualIssue(
                        analysis_run_id=analysis_run_id,
                        company_id=company_id,
                        store_id=store_id,
                        image_id=image_id,
                        expected_product_id=exp.id,
                        issue_type=ExpectedActualIssueType.EXCESS_PRODUCT,
                        severity=ExpectedActualIssueSeverity.LOW,
                        message=f"Expected product '{exp.product_name}' has excess stock (Observed: {obs_qty}, Max Allowed: {exp.expected_max_quantity}).",
                        evidence_references=obs_refs
                    )
                )
            else:
                item_status = ExpectedActualItemStatus.OBSERVED

            items.append(
                ExpectedActualItem(
                    analysis_run_id=analysis_run_id,
                    company_id=company_id,
                    expected_product_id=exp.id,
                    product_code=exp.product_code,
                    product_name=exp.product_name,
                    expected_quantity=exp.expected_quantity,
                    expected_min_quantity=exp.expected_min_quantity,
                    expected_max_quantity=exp.expected_max_quantity,
                    observed_quantity=obs_qty,
                    difference=diff,
                    status=item_status,
                    evidence_references=obs_refs
                )
            )

        # Process Unmatched Detections -> UNEXPECTED or UNMATCHED items & issues
        for un_det in unmatched_detections:
            un_ref = [{
                "detection_id": str(un_det.id),
                "class_name": un_det.class_name,
                "confidence": un_det.confidence,
                "bounding_box": un_det.bounding_box.model_dump(),
                "related_ocr": un_det.spatial_relationships
            }]

            # Determine whether it's an UNEXPECTED observation or UNMATCHED evidence
            item_status = ExpectedActualItemStatus.UNEXPECTED if expectations else ExpectedActualItemStatus.UNMATCHED
            issue_type = ExpectedActualIssueType.UNEXPECTED_PRODUCT if expectations else ExpectedActualIssueType.UNMATCHED_OBSERVATION
            msg = f"Observed item '{un_det.class_name}' has no active expectation configuration." if expectations else f"Unmatched evidence detected: '{un_det.class_name}'."

            items.append(
                ExpectedActualItem(
                    analysis_run_id=analysis_run_id,
                    company_id=company_id,
                    expected_product_id=None,
                    product_code=un_det.class_name.upper(),
                    product_name=un_det.class_name,
                    expected_quantity=0,
                    expected_min_quantity=0,
                    expected_max_quantity=0,
                    observed_quantity=1,
                    difference=1,
                    status=item_status,
                    evidence_references=un_ref
                )
            )

            issues.append(
                ExpectedActualIssue(
                    analysis_run_id=analysis_run_id,
                    company_id=company_id,
                    store_id=store_id,
                    image_id=image_id,
                    expected_product_id=None,
                    issue_type=issue_type,
                    severity=ExpectedActualIssueSeverity.LOW,
                    message=msg,
                    evidence_references=un_ref
                )
            )

        return items, issues
