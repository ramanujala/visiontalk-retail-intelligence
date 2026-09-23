"""Evidence Engine Domain Exceptions."""

from app.core.exceptions import VisionTalkException


class EvidenceError(VisionTalkException):
    """Base exception for Evidence Engine domain errors."""
    pass


class EvidenceNotFoundError(EvidenceError):
    """Raised when evidence or requested analysis resources do not exist or are cross-tenant."""
    pass


class EvidenceGenerationError(EvidenceError):
    """Raised when canonical evidence aggregation fails."""
    pass
