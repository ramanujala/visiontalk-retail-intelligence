import re
from typing import Tuple, List, Dict
from app.schemas.question_router import QuestionIntent


class IntentClassifier:
    """
    Lightweight, deterministic first-stage intent classifier using normalized pattern matching.
    Provides fast, explainable, and predictable routing without requiring LLM calls.
    """

    COUNT_PATTERNS = [
        r"\bhow\s+many\b",
        r"\bcount\b",
        r"\btotal\s+number\s+of\b",
        r"\bquantity\b",
        r"\bunits\b",
        r"\bhow\s+much\s+stock\b",
        r"\bnumber\s+of\s+items\b",
        r"\bhow\s+many\s+products\b"
    ]

    AVAILABILITY_PATTERNS = [
        r"\bis\s+.*(available|present|in\s+stock|on\s+shelf)\b",
        r"\bare\s+.*(available|present|in\s+stock|on\s+shelf)\b",
        r"\bdo\s+we\s+have\b",
        r"\bis\s+there\s+any\b",
        r"\bcan\s+you\s+find\b",
        r"\bcheck\s+presence\b",
        r"\bpresence\s+of\b"
    ]

    EXPECTED_VS_ACTUAL_PATTERNS = [
        r"\bmissing\b",
        r"\bunexpected\b",
        r"\bextra\b",
        r"\bplanogram\b",
        r"\bexpected\b",
        r"\bdiscrepan(cy|cies)\b",
        r"\bstockout\b",
        r"\blow\s+stock\b",
        r"\boverstock\b",
        r"\bvariance\b",
        r"\bdiffer(ence|ent)\b"
    ]

    COMPLIANCE_PATTERNS = [
        r"\bcomplian(ce|t)\b",
        r"\bviolat(ion|ions)\b",
        r"\brule\b",
        r"\brules\b",
        r"\bpass\b",
        r"\bfail\b",
        r"\bwarning\b",
        r"\bseverity\b",
        r"\baudit\s+score\b",
        r"\bzone\b",
        r"\bplacement\b"
    ]

    GENERAL_PATTERNS = [
        r"\bexplain\b",
        r"\bsummarize\b",
        r"\bsummary\b",
        r"\boverview\b",
        r"\bwhat\s+does\s+this\s+shelf\s+look\s+like\b",
        r"\btell\s+me\s+about\b",
        r"\bdescription\b"
    ]

    def classify(self, question: str) -> Tuple[QuestionIntent, str, float, str, str]:
        """
        Classifies a raw text question into a QuestionIntent.
        Returns tuple: (QuestionIntent, route, confidence, reason, target_service)
        """
        if not question or not question.strip():
            return (
                QuestionIntent.UNKNOWN,
                "unknown",
                0.0,
                "Empty or whitespace-only question string.",
                "None"
            )

        # 1. Normalize whitespace & lower-case
        normalized = " ".join(question.strip().lower().split())

        # 2. Check COUNT
        for pattern in self.COUNT_PATTERNS:
            if re.search(pattern, normalized):
                return (
                    QuestionIntent.COUNT,
                    "detections",
                    0.95,
                    f"Matched count query pattern '{pattern}'",
                    "DetectionEngine / EvidenceEngine"
                )

        # 3. Check EXPECTED_VS_ACTUAL
        for pattern in self.EXPECTED_VS_ACTUAL_PATTERNS:
            if re.search(pattern, normalized):
                return (
                    QuestionIntent.EXPECTED_VS_ACTUAL,
                    "expected_vs_actual",
                    0.95,
                    f"Matched planogram expectation pattern '{pattern}'",
                    "ExpectedActualEngine"
                )

        # 4. Check COMPLIANCE
        for pattern in self.COMPLIANCE_PATTERNS:
            if re.search(pattern, normalized):
                return (
                    QuestionIntent.COMPLIANCE,
                    "compliance",
                    0.95,
                    f"Matched compliance rule pattern '{pattern}'",
                    "ComplianceEngine"
                )

        # 5. Check AVAILABILITY
        for pattern in self.AVAILABILITY_PATTERNS:
            if re.search(pattern, normalized):
                return (
                    QuestionIntent.AVAILABILITY,
                    "availability",
                    0.90,
                    f"Matched item availability pattern '{pattern}'",
                    "DetectionEngine / ExpectedActualEngine"
                )

        # 6. Check GENERAL EXPLANATION
        for pattern in self.GENERAL_PATTERNS:
            if re.search(pattern, normalized):
                return (
                    QuestionIntent.GENERAL,
                    "llm_explanation",
                    0.90,
                    f"Matched general explanation pattern '{pattern}'",
                    "LLMService"
                )

        # 7. Default Fallback / Ambiguous -> GENERAL via LLM
        return (
            QuestionIntent.GENERAL,
            "llm_explanation",
            0.60,
            "No specific deterministic rule pattern matched. Routing to grounded LLM reasoning.",
            "LLMService"
        )
