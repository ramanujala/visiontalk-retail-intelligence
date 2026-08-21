import pytest
from fastapi.testclient import TestClient
from app.core.database import check_database_health


@pytest.mark.integration
def test_readiness_endpoint_integration(client: TestClient):
    """Integration test verifying /api/v1/health/ready readiness check against PostgreSQL status."""
    response = client.get("/api/v1/health/ready")
    is_healthy = check_database_health()
    if is_healthy:
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["database_connected"] is True
    else:
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["database_connected"] is False


@pytest.mark.integration
def test_database_connection_integration():
    """Integration test verifying database connectivity checker execution."""
    is_healthy = check_database_health()
    assert isinstance(is_healthy, bool)
