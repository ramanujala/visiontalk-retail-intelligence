import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.services.llm_context import build_grounded_llm_context
from app.services.grounding_prompt_builder import build_grounding_prompt

logger = logging.getLogger(__name__)


class LLMService:
    """
    Dedicated wrapper around the official Google GenAI SDK (`google-genai`).
    Isolates Gemini LLM communication, grounding prompt construction, and low-confidence fallback handling.
    """

    def __init__(self):
        self.enabled = settings.GEMINI_ENABLED
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None

    def _get_client(self):
        """Lazy initialization of the official google-genai Client."""
        if self._client is None:
            if not self.api_key:
                logger.warning("GEMINI_API_KEY is not configured. GenAI client initialization skipped.")
                return None
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                logger.error("google-genai package is not installed.")
                return None
            except Exception as e:
                logger.error(f"Failed to initialize google-genai Client: {str(e)}")
                return None
        return self._client

    def generate_explanation(
        self,
        image: Any,
        evidence_data: Optional[Dict[str, Any]] = None,
        expected_actual_data: Optional[Dict[str, Any]] = None,
        compliance_data: Optional[Dict[str, Any]] = None,
        question_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a grounded natural language explanation from structured deterministic evidence.
        Enforces low-confidence fallback, error isolation, and evidence traceability.
        """
        # 1. Build structured context payload
        context_payload = build_grounded_llm_context(
            image=image,
            evidence_data=evidence_data,
            expected_actual_data=expected_actual_data,
            compliance_data=compliance_data,
        )

        # 2. Compute evidence confidence score
        detections = (evidence_data or {}).get("detections", [])
        if detections:
            avg_conf = sum(d.get("confidence", 0.0) for d in detections) / len(detections)
        else:
            avg_conf = 0.5  # Neutral baseline if no detections exist

        # Collect evidence references for traceability
        evidence_refs = {
            "image_id": str(image.id),
            "detection_count": len(detections),
            "ocr_count": len((evidence_data or {}).get("ocr_results", [])),
            "compliance_findings_count": len((compliance_data or {}).get("findings", [])),
        }

        # 3. Check for low-confidence fallback condition
        if avg_conf < settings.LLM_MIN_CONFIDENCE_THRESHOLD:
            logger.info(f"Low confidence evidence score ({avg_conf:.2f} < {settings.LLM_MIN_CONFIDENCE_THRESHOLD}). Triggering fallback.")
            return {
                "status": "FALLBACK",
                "explanation": "The visual shelf evidence collected has low detection confidence score. Automatic Gemini explanation is restricted to prevent ungrounded inferences. Please review raw perception overlay evidence.",
                "key_findings": [
                    "Visual detection confidence is below required threshold.",
                    f"Observed average confidence score: {avg_conf:.2f}",
                ],
                "evidence_references": evidence_refs,
                "confidence": round(avg_conf, 3),
                "fallback_reason": "LOW_CONFIDENCE",
                "model": self.model_name,
                "created_at": datetime.now(timezone.utc),
            }

        # 4. Check if Gemini service is disabled or unconfigured
        if not self.enabled or not self.api_key:
            logger.info("Gemini LLM is disabled or API key is missing. Returning safe default explanation.")
            key_findings = []
            if compliance_data and compliance_data.get("findings"):
                for f in compliance_data["findings"]:
                    key_findings.append(f"{f.get('severity')}: {f.get('message')}")
            else:
                key_findings.append(f"Detected {len(detections)} items on shelf.")

            return {
                "status": "FALLBACK",
                "explanation": "Deterministic analysis complete. (Gemini LLM explanation layer is currently disabled in configuration).",
                "key_findings": key_findings,
                "evidence_references": evidence_refs,
                "confidence": round(avg_conf, 3),
                "fallback_reason": "GEMINI_DISABLED" if not self.enabled else "MISSING_API_KEY",
                "model": self.model_name,
                "created_at": datetime.now(timezone.utc),
            }

        # 5. Build Grounding Prompt
        prompt = build_grounding_prompt(context_payload, question_context=question_context)

        # 6. Call Google GenAI SDK safely
        client = self._get_client()
        if not client:
            return {
                "status": "FALLBACK",
                "explanation": "Google GenAI SDK client could not be initialized.",
                "key_findings": ["GenAI SDK initialization failure."],
                "evidence_references": evidence_refs,
                "confidence": round(avg_conf, 3),
                "fallback_reason": "CLIENT_INIT_FAILED",
                "model": self.model_name,
                "created_at": datetime.now(timezone.utc),
            }

        try:
            from google.genai import types

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
                ),
            )

            raw_text = response.text if response and hasattr(response, "text") else "No explanation generated."
            
            # Extract bullet point key findings from generated text
            key_findings = []
            for line in raw_text.split("\n"):
                cleaned = line.strip(" *-•")
                if cleaned and (line.strip().startswith("-") or line.strip().startswith("*") or line.strip().startswith("•")):
                    key_findings.append(cleaned)

            if not key_findings:
                key_findings = ["Analysis grounded on verified shelf evidence."]

            return {
                "status": "EXPLAINED",
                "explanation": raw_text,
                "key_findings": key_findings,
                "evidence_references": evidence_refs,
                "confidence": round(avg_conf, 3),
                "fallback_reason": None,
                "model": self.model_name,
                "created_at": datetime.now(timezone.utc),
            }

        except Exception as e:
            logger.error(f"Gemini API invocation error: {str(e)}")
            return {
                "status": "FALLBACK",
                "explanation": "An error occurred while contacting the Gemini LLM service. Deterministic analysis results remain valid.",
                "key_findings": ["Gemini service provider error."],
                "evidence_references": evidence_refs,
                "confidence": round(avg_conf, 3),
                "fallback_reason": f"PROVIDER_ERROR: {str(e)}",
                "model": self.model_name,
                "created_at": datetime.now(timezone.utc),
            }


llm_service = LLMService()
