import logging
from typing import Optional
from app.schemas.question_router import QuestionRouteRequest, QuestionRouteResult, QuestionIntent
from app.services.intent_classifier import IntentClassifier

logger = logging.getLogger(__name__)


class QuestionRouter:
    """
    Core Question Router Orchestrator for Phase 10.
    Directs incoming retail audit questions to the appropriate capability service based on deterministic intent classification.
    """

    def __init__(self, classifier: Optional[IntentClassifier] = None):
        self.classifier = classifier or IntentClassifier()

    def route_question(self, request: QuestionRouteRequest) -> QuestionRouteResult:
        """
        Processes a QuestionRouteRequest and returns a structured QuestionRouteResult.
        """
        intent, route, confidence, reason, target_service = self.classifier.classify(request.question)

        logger.info(f"Question routed: intent={intent}, route={route}, confidence={confidence:.2f}")

        return QuestionRouteResult(
            question=request.question,
            intent=intent,
            route=route,
            confidence=confidence,
            reason=reason,
            target_service=target_service
        )


question_router = QuestionRouter()
