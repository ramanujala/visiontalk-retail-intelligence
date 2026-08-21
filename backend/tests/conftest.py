import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Test client fixture for FastAPI app."""
    with TestClient(app) as c:
        yield c
