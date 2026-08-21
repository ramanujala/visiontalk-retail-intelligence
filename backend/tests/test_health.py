from fastapi.testclient import TestClient
from app.core.config import settings
from app.services.storage.local import LocalStorageProvider
import os
import shutil


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to VisionTalk" in data["message"]
    assert data["version"] == settings.VERSION


def test_liveness_endpoint(client: TestClient):
    """Verifies that /api/v1/health liveness check returns 200 without DB dependency."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == settings.VERSION
    assert "timestamp" in data


def test_cors_configuration():
    """Verifies CORS origins parsing logic."""
    from app.core.config import Settings
    custom_settings = Settings(CORS_ORIGINS="http://test1.com, http://test2.com")
    assert custom_settings.CORS_ORIGINS == ["http://test1.com", "http://test2.com"]


def test_local_storage_abstraction(tmp_path):
    """Verifies StorageService architectural abstraction works with LocalStorageProvider."""
    storage = LocalStorageProvider(base_dir=str(tmp_path))
    test_content = b"sample image binary stream"
    
    import io
    file_stream = io.BytesIO(test_content)
    
    saved_path = storage.save_file(file_stream, filename="test_shelf.jpg", destination_folder="sample")
    assert storage.file_exists(saved_path)
    
    retrieved = storage.get_file(saved_path)
    assert retrieved == test_content
    
    deleted = storage.delete_file(saved_path)
    assert deleted is True
    assert not storage.file_exists(saved_path)
