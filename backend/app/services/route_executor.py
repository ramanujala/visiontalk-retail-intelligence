import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.image import Image
from app.models.analysis import AnalysisRun, AnalysisType
from app.schemas.question_router import QuestionRouteResult, QuestionIntent
from app.services.evidence.engine import EvidenceEngine
from app.services.expected_actual import ExpectedActualEngine
from app.services.compliance_engine import ComplianceEngine
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class RouteExecutor:
    """
    Orchestrates execution of the selected route capability identified by the QuestionRouter.
    Delegates to Phase 4-9 services and returns normalized answer text and metadata.
    """

    def __init__(self, db: Session):
        self.db = db

    def execute_route(
        self,
        route_result: QuestionRouteResult,
        image: Optional[Image],
        company_id: Any,
        user_id: Any,
        user_question: str
    ) -> Dict[str, Any]:
        intent = route_result.intent

        # 1. Image required for image-dependent perception routes
        if not image and intent in [QuestionIntent.COUNT, QuestionIntent.AVAILABILITY, QuestionIntent.EXPECTED_VS_ACTUAL, QuestionIntent.COMPLIANCE]:
            return {
                "answer": f"To evaluate {intent.value} for your question ('{user_question}'), please attach or select a retail shelf image.",
                "metadata": {"intent": intent.value, "route": route_result.route, "error": "MISSING_IMAGE_CONTEXT"}
            }

        # 2. Route Execution
        if intent == QuestionIntent.COUNT and image:
            ev_engine = EvidenceEngine(self.db)
            try:
                evidence = ev_engine.generate_canonical_evidence(image.id, company_id)
                detections = evidence.detections or []
                count = len(detections)
                class_counts = {}
                for d in detections:
                    cls = d.class_name
                    class_counts[cls] = class_counts.get(cls, 0) + 1

                summary_str = ", ".join([f"{k}: {v}" for k, v in class_counts.items()]) if class_counts else "No objects detected."
                return {
                    "answer": f"Observed a total of {count} product items on the shelf image ({summary_str}).",
                    "metadata": {"total_count": count, "class_breakdown": class_counts, "detection_ids": [str(d.id) for d in detections]}
                }
            except Exception as e:
                return {"answer": f"Could not compute count evidence: {str(e)}", "metadata": {"error": str(e)}}

        elif intent == QuestionIntent.EXPECTED_VS_ACTUAL and image:
            ea_engine = ExpectedActualEngine(self.db)
            try:
                ea_res = ea_engine.analyze(image.id, company_id, user_id, force_reanalyze=False)
                missing = [item.product_name or item.product_code for item in ea_res.items if item.status == "MISSING"]
                unexpected = [item.product_name or item.product_code for item in ea_res.items if item.status == "UNEXPECTED"]

                answer_lines = [f"Expected vs Actual Planogram Summary (Total SKUs: {ea_res.total_expected_skus}):"]
                if missing:
                    answer_lines.append(f"• Missing expected products ({len(missing)}): {', '.join(missing)}")
                if unexpected:
                    answer_lines.append(f"• Unexpected products ({len(unexpected)}): {', '.join(unexpected)}")
                if not missing and not unexpected:
                    answer_lines.append("• All expected planogram products are in full compliance!")

                return {
                    "answer": "\n".join(answer_lines),
                    "metadata": {
                        "missing_count": ea_res.missing_count,
                        "unexpected_count": ea_res.unexpected_count,
                        "observed_count": ea_res.total_observed_units
                    }
                }
            except Exception as e:
                return {"answer": f"Could not perform expected vs actual analysis: {str(e)}", "metadata": {"error": str(e)}}

        elif intent == QuestionIntent.COMPLIANCE and image:
            comp_engine = ComplianceEngine(self.db)
            try:
                comp_summary = comp_engine.get_compliance_summary(image.id, company_id)
                findings = comp_summary.findings or []
                failed = [f for f in findings if f.status == "FAIL"]

                if failed:
                    findings_str = "\n".join([f"• [{f.severity}] {f.rule_name}: {f.message}" for f in failed])
                    answer = f"Shelf compliance evaluation status: {len(failed)} violation(s) detected out of {comp_summary.total_rules} configured rules:\n{findings_str}"
                else:
                    answer = f"Shelf compliance evaluation status: All {comp_summary.total_rules} active compliance rules PASSED clean!"

                return {
                    "answer": answer,
                    "metadata": {
                        "total_rules": comp_summary.total_rules,
                        "passed": comp_summary.passed,
                        "failed": comp_summary.failed
                    }
                }
            except Exception as e:
                return {"answer": f"Could not perform compliance check: {str(e)}", "metadata": {"error": str(e)}}

        elif intent == QuestionIntent.AVAILABILITY and image:
            ev_engine = EvidenceEngine(self.db)
            try:
                evidence = ev_engine.generate_canonical_evidence(image.id, company_id)
                detections = evidence.detections or []
                classes = list(set(d.class_name for d in detections))
                if classes:
                    answer = f"Item availability check: Currently detected active products on shelf include: {', '.join(classes)}."
                else:
                    answer = "Item availability check: No active products were detected on the shelf."
                return {"answer": answer, "metadata": {"available_classes": classes}}
            except Exception as e:
                return {"answer": f"Availability evaluation error: {str(e)}", "metadata": {"error": str(e)}}

        # Fallback / GENERAL / UNKNOWN -> Grounded Gemini LLM explanation
        if image:
            try:
                ev_engine = EvidenceEngine(self.db)
                evidence = ev_engine.generate_canonical_evidence(image.id, company_id).model_dump(mode="json")
            except Exception:
                evidence = None

            try:
                ea_engine = ExpectedActualEngine(self.db)
                expected_actual = ea_engine.analyze(image.id, company_id, user_id, force_reanalyze=False).model_dump(mode="json")
            except Exception:
                expected_actual = None

            try:
                comp_engine = ComplianceEngine(self.db)
                compliance = comp_engine.get_compliance_summary(image.id, company_id).model_dump(mode="json")
            except Exception:
                compliance = None

            llm_res = llm_service.generate_explanation(
                image=image,
                evidence_data=evidence,
                expected_actual_data=expected_actual,
                compliance_data=compliance,
                question_context=user_question
            )
            return {
                "answer": llm_res["explanation"],
                "metadata": {
                    "key_findings": llm_res["key_findings"],
                    "confidence": llm_res["confidence"],
                    "fallback_reason": llm_res.get("fallback_reason")
                }
            }

        return {
            "answer": f"Received inquiry: '{user_question}'. Please specify an image for detailed computer vision evidence analysis.",
            "metadata": {"intent": intent.value}
        }
