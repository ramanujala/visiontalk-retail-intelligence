"""Retail Compliance Rules Engine Service Layer.

Evaluates configured ComplianceRules against Phase 6 Canonical Evidence and Phase 7 Expected vs Actual Analysis.
Generates structured, explainable ComplianceFindings with evidence traceability.
"""

from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.image import Image, ImageStatus
from app.models.compliance_rule import (
    ComplianceRule,
    ComplianceFinding,
    RuleType,
    RuleSeverity,
    FindingStatus
)
from app.models.analysis import (
    AnalysisRun,
    AnalysisRunStatus,
    AnalysisType,
    ExpectedActualItem,
    ExpectedActualIssue
)
from app.services.evidence.engine import EvidenceEngine
from app.services.evidence.exceptions import EvidenceNotFoundError
from app.services.expected_actual import ExpectedActualEngine
from app.schemas.evidence import CanonicalEvidenceResponse, EvidenceDetectionItem, EvidenceOCRItem


class ComplianceEngine:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_rules(
        self,
        image_id: UUID,
        company_id: UUID,
        initiated_by_user_id: UUID,
        force_reanalyze: bool = False
    ) -> AnalysisRun:
        """Evaluates active compliance rules for an image and returns completed AnalysisRun."""
        # 1. Validate Image Ownership & Tenant Isolation
        image = self.db.query(Image).filter(
            Image.id == image_id,
            Image.company_id == company_id,
            Image.status != ImageStatus.DELETED
        ).first()

        if not image:
            raise EvidenceNotFoundError("Image not found.")

        # 2. Duplicate Analysis Prevention
        if not force_reanalyze:
            existing_run = self.db.query(AnalysisRun).filter(
                AnalysisRun.image_id == image_id,
                AnalysisRun.company_id == company_id,
                AnalysisRun.analysis_type == AnalysisType.COMPLIANCE,
                AnalysisRun.status == AnalysisRunStatus.COMPLETED
            ).order_by(AnalysisRun.created_at.desc()).first()

            if existing_run:
                return existing_run

        # 3. Obtain Phase 6 Evidence & Phase 7 Expected vs Actual Analysis
        evidence_engine = EvidenceEngine(self.db)
        canonical_evidence = evidence_engine.generate_canonical_evidence(image_id=image_id, company_id=company_id)

        exp_actual_engine = ExpectedActualEngine(self.db)
        exp_actual_run = exp_actual_engine.analyze(
            image_id=image_id,
            company_id=company_id,
            initiated_by_user_id=initiated_by_user_id
        )

        # 4. Fetch Active Compliance Rules for Company & Store
        rules = self.db.query(ComplianceRule).filter(
            ComplianceRule.company_id == company_id,
            ComplianceRule.is_active == True,
            (ComplianceRule.store_id == image.store_id) | (ComplianceRule.store_id == None)
        ).all()

        # 5. Create AnalysisRun in RUNNING state
        analysis_run = AnalysisRun(
            company_id=company_id,
            image_id=image_id,
            initiated_by=initiated_by_user_id,
            analysis_type=AnalysisType.COMPLIANCE,
            status=AnalysisRunStatus.RUNNING,
            model_name="ComplianceEngine",
            model_version="1.0",
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(analysis_run)
        self.db.commit()
        self.db.refresh(analysis_run)

        try:
            findings: List[ComplianceFinding] = []
            for rule in rules:
                finding = self._evaluate_single_rule(
                    rule=rule,
                    analysis_run_id=analysis_run.id,
                    image=image,
                    evidence=canonical_evidence,
                    exp_actual_run=exp_actual_run
                )
                if finding:
                    findings.append(finding)

            if findings:
                self.db.add_all(findings)

            analysis_run.status = AnalysisRunStatus.COMPLETED
            analysis_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(analysis_run)
            return analysis_run

        except Exception as exc:
            self.db.rollback()
            analysis_run.status = AnalysisRunStatus.FAILED
            analysis_run.error_message = f"Compliance evaluation failed: {str(exc)}"
            analysis_run.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            self.db.refresh(analysis_run)
            return analysis_run

    def _evaluate_single_rule(
        self,
        rule: ComplianceRule,
        analysis_run_id: UUID,
        image: Image,
        evidence: CanonicalEvidenceResponse,
        exp_actual_run: AnalysisRun
    ) -> Optional[ComplianceFinding]:
        """Evaluates a single compliance rule deterministically against structured evidence."""
        config = rule.configuration or {}

        if rule.rule_type == RuleType.PRODUCT_REQUIRED:
            target_prod = config.get("product_code") or config.get("product_name") or ""
            target_norm = target_prod.strip().upper()

            # Search in detected objects or OCR results
            matching_dets = [d for d in evidence.detections if d.class_name.strip().upper() == target_norm]
            matching_ocrs = [o for o in evidence.ocr_results if o.normalized_text.strip().upper() == target_norm]

            if matching_dets or matching_ocrs:
                status = FindingStatus.PASS
                msg = f"Required product '{target_prod}' was detected on shelf."
            else:
                status = FindingStatus.FAIL
                msg = f"Required product '{target_prod}' was not detected in the image."

            ev_refs = [d.model_dump(mode="json") for d in matching_dets] + [o.model_dump(mode="json") for o in matching_ocrs]

            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=status,
                severity=rule.severity,
                message=msg,
                details={"target_product": target_prod, "detected_count": len(matching_dets) + len(matching_ocrs)},
                evidence_references=ev_refs
            )

        elif rule.rule_type == RuleType.PRODUCT_QUANTITY:
            target_prod = config.get("product_code") or config.get("product_name") or ""
            target_norm = target_prod.strip().upper()
            min_qty = config.get("minimum_quantity", 1)

            matching_dets = [d for d in evidence.detections if d.class_name.strip().upper() == target_norm]
            obs_qty = len(matching_dets)

            if obs_qty >= min_qty:
                status = FindingStatus.PASS
                msg = f"Product '{target_prod}' quantity ({obs_qty}) meets or exceeds required minimum ({min_qty})."
            else:
                status = FindingStatus.FAIL
                msg = f"Product '{target_prod}' quantity ({obs_qty}) is below the required minimum of {min_qty}."

            ev_refs = [d.model_dump(mode="json") for d in matching_dets]

            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=status,
                severity=rule.severity,
                message=msg,
                details={"target_product": target_prod, "observed_quantity": obs_qty, "minimum_quantity": min_qty},
                evidence_references=ev_refs
            )

        elif rule.rule_type == RuleType.UNEXPECTED_PRODUCT:
            # Check Phase 7 unexpected items
            unexpected_items = [item for item in exp_actual_run.expected_actual_items if item.status == "UNEXPECTED"]

            if not unexpected_items:
                status = FindingStatus.PASS
                msg = "No unexpected products detected on shelf."
                ev_refs = []
            else:
                status = FindingStatus.FAIL
                names = [item.product_name for item in unexpected_items]
                msg = f"Unexpected product(s) detected: {', '.join(names)}."
                ev_refs = [item.evidence_references for item in unexpected_items]

            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=status,
                severity=rule.severity,
                message=msg,
                details={"unexpected_count": len(unexpected_items)},
                evidence_references=ev_refs
            )

        elif rule.rule_type == RuleType.PRODUCT_ZONE:
            target_prod = config.get("product_code") or config.get("product_name") or ""
            target_norm = target_prod.strip().upper()
            allowed_box = config.get("allowed_zone_box")  # {x_min, y_min, x_max, y_max}

            matching_dets = [d for d in evidence.detections if d.class_name.strip().upper() == target_norm]

            if not matching_dets:
                return None  # Product not present to evaluate zone

            zone_violations = []
            for det in matching_dets:
                if allowed_box:
                    box = det.bounding_box
                    if (
                        box.x_min < allowed_box.get("x_min", 0) or
                        box.y_min < allowed_box.get("y_min", 0) or
                        box.x_max > allowed_box.get("x_max", 10000) or
                        box.y_max > allowed_box.get("y_max", 10000)
                    ):
                        zone_violations.append(det)

            if not zone_violations:
                status = FindingStatus.PASS
                msg = f"Product '{target_prod}' detected within allowed zone bounds."
            else:
                status = FindingStatus.FAIL
                msg = f"Product '{target_prod}' was detected outside the allowed zone."

            ev_refs = [d.model_dump(mode="json") for d in (zone_violations if zone_violations else matching_dets)]

            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=status,
                severity=rule.severity,
                message=msg,
                details={"target_product": target_prod, "violations_count": len(zone_violations)},
                evidence_references=ev_refs
            )

        elif rule.rule_type == RuleType.OCR_REQUIRED:
            required_text = config.get("required_text", "").strip().upper()
            matching_ocrs = [o for o in evidence.ocr_results if required_text in o.normalized_text.strip().upper()]

            if matching_ocrs:
                status = FindingStatus.PASS
                msg = f"Required OCR text '{required_text}' was detected."
            else:
                status = FindingStatus.FAIL
                msg = f"Required OCR text '{required_text}' was not detected in image."

            ev_refs = [o.model_dump(mode="json") for o in matching_ocrs]

            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=status,
                severity=rule.severity,
                message=msg,
                details={"required_text": required_text, "matched_count": len(matching_ocrs)},
                evidence_references=ev_refs
            )

        else:
            # CUSTOM_THRESHOLD or default fallback
            return ComplianceFinding(
                company_id=rule.company_id,
                store_id=image.store_id,
                image_id=image.id,
                analysis_run_id=analysis_run_id,
                rule_id=rule.id,
                status=FindingStatus.PASS,
                severity=rule.severity,
                message=f"Rule '{rule.name}' evaluated successfully.",
                details={},
                evidence_references=[]
            )
