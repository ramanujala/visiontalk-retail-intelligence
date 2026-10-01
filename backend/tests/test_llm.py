import pytest
from unittest.mock import MagicMock, patch
from fastapi import status
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, AnalysisType, AnalysisRunStatus
from app.core.security import hash_password, create_access_token
from app.services.llm_service import LLMService


@pytest.fixture
def llm_test_setup(db_session):
    company_a = Company(name="LLM Company A", slug="llm-company-a")
    company_b = Company(name="LLM Company B", slug="llm-company-b")
    db_session.add_all([company_a, company_b])
    db_session.flush()

    user_a = User(
        company_id=company_a.id,
        email="user_a@llm.com",
        password_hash=hash_password("password123"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    user_b = User(
        company_id=company_b.id,
        email="user_b@llm.com",
        password_hash=hash_password("password123"),
        full_name="User B",
        role=UserRole.ADMIN
    )
    db_session.add_all([user_a, user_b])
    db_session.flush()

    store_a = Store(company_id=company_a.id, name="Store A", code="SA")
    db_session.add(store_a)
    db_session.flush()

    image_a = Image(
        company_id=company_a.id,
        store_id=store_a.id,
        uploaded_by=user_a.id,
        original_filename="shelf_a.jpg",
        storage_key="llm/shelf_a.jpg",
        file_size=1000,
        mime_type="image/jpeg",
        width=1000,
        height=1000,
        checksum="hash_a",
        quality_score=90,
        status=ImageStatus.READY
    )
    image_b = Image(
        company_id=company_b.id,
        store_id=store_a.id,
        uploaded_by=user_b.id,
        original_filename="shelf_b.jpg",
        storage_key="llm/shelf_b.jpg",
        file_size=1000,
        mime_type="image/jpeg",
        width=1000,
        height=1000,
        checksum="hash_b",
        quality_score=90,
        status=ImageStatus.READY
    )
    db_session.add_all([image_a, image_b])
    db_session.commit()

    token_a = create_access_token(data={"sub": str(user_a.id), "company_id": str(company_a.id), "role": user_a.role})

    return {
        "company_a": company_a,
        "company_b": company_b,
        "user_a": user_a,
        "user_b": user_b,
        "image_a": image_a,
        "image_b": image_b,
        "headers_a": {"Authorization": f"Bearer {token_a}"}
    }


def test_llm_service_fallback_on_low_confidence(llm_test_setup):
    """Test LLMService generates FALLBACK response when evidence confidence is low."""
    service = LLMService()
    evidence_low = {
        "detections": [
            {"id": "det-1", "class_name": "bottle", "confidence": 0.10}
        ],
        "ocr_results": []
    }
    result = service.generate_explanation(image=llm_test_setup["image_a"], evidence_data=evidence_low)
    
    assert result["status"] == "FALLBACK"
    assert result["fallback_reason"] == "LOW_CONFIDENCE"
    assert result["confidence"] == 0.10


def test_llm_service_fallback_when_disabled(llm_test_setup):
    """Test LLMService generates safe FALLBACK when Gemini is disabled."""
    service = LLMService()
    service.enabled = False
    evidence = {
        "detections": [
            {"id": "det-1", "class_name": "bottle", "confidence": 0.90}
        ]
    }
    result = service.generate_explanation(image=llm_test_setup["image_a"], evidence_data=evidence)
    
    assert result["status"] == "FALLBACK"
    assert result["fallback_reason"] == "GEMINI_DISABLED"


@patch("app.services.llm_service.LLMService._get_client")
def test_llm_explanation_api_success(mock_get_client, client, llm_test_setup):
    """Test POST /api/v1/llm/explain/{image_id} returns structured explanation response."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "- Verified 1 bottle on top shelf.\n- No compliance issues detected."
    mock_client.models.generate_content.return_value = mock_response
    mock_get_client.return_value = mock_client

    response = client.post(
        f"/api/v1/llm/explain/{llm_test_setup['image_a'].id}",
        json={"force_reanalyze": True, "question_context": "Check bottles"},
        headers=llm_test_setup["headers_a"]
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    
    assert data["image_id"] == str(llm_test_setup["image_a"].id)
    assert data["status"] in ["EXPLAINED", "FALLBACK"]
    assert len(data["key_findings"]) > 0


def test_llm_explanation_tenant_isolation(client, llm_test_setup):
    """Test Company A cannot request LLM explanation for Company B image."""
    response = client.post(
        f"/api/v1/llm/explain/{llm_test_setup['image_b'].id}",
        headers=llm_test_setup["headers_a"]
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
