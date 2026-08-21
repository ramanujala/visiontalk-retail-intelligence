from datetime import datetime, timezone
from fastapi import APIRouter, status, Response
from app.core.config import settings
from app.core.database import check_database_health
from app.schemas.health import LivenessResponse, ReadinessResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=LivenessResponse, summary="Application Liveness Check")
def get_liveness():
    """Lightweight application liveness check. Does NOT depend on external services."""
    return LivenessResponse(
        status="healthy",
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat()
    )


@router.get("/ready", response_model=ReadinessResponse, summary="Application Readiness Check")
def get_readiness(response: Response):
    """Application readiness check verifying PostgreSQL database connectivity."""
    db_healthy = check_database_health()
    
    if not db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="unhealthy",
            database_connected=False,
            version=settings.VERSION,
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    return ReadinessResponse(
        status="ready",
        database_connected=True,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
