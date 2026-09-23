import pytest
import os
import uuid
from unittest.mock import MagicMock, patch
from PIL import Image as PILImage

from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, OCRResult, AnalysisRunStatus, AnalysisType
from app.core.security import hash_password, create_access_token
from app.services.detection.schemas import BoundingBox
from app.services.ocr.schemas import OCREvidence, OCRResultItem
from app.services.ocr.exceptions import OCRInferenceError, OCRDependencyError


def create_test_image_file(storage_dir, company_id, store_id):
    """Helper to create physical image on disk and returns (image_id, storage_key)."""
    image_id = uuid.uuid4()
    rel_folder = f"{company_id}/{store_id}"
    target_dir = os.path.join(storage_dir, rel_folder)
    os.makedirs(target_dir, exist_ok=True)
    filename = f"{image_id}.jpg"
    full_path = os.path.join(target_dir, filename)

    img = PILImage.new("RGB", (400, 300), color="white")
    img.save(full_path, "JPEG")

    storage_key = os.path.normpath(os.path.join(rel_folder, filename)).replace("\\", "/")
    return image_id, storage_key


@pytest.fixture
def setup_tenants_and_images(db_session, tmp_path):
    """Sets up Company A and Company B with users, stores, and stored images."""
    storage_dir = str(tmp_path / "storage_uploads")

    # Company A
    comp_a = Company(name="Alpha Corp", slug="alpha-corp")
    db_session.add(comp_a)
    db_session.flush()

    user_a_admin = User(
        company_id=comp_a.id,
        email="admin@alpha.com",
        password_hash=hash_password("password123"),
        full_name="Alpha Admin",
        role=UserRole.ADMIN
    )
    user_a_staff = User(
        company_id=comp_a.id,
        email="staff@alpha.com",
        password_hash=hash_password("password123"),
        full_name="Alpha Staff",
        role=UserRole.STAFF
    )
    store_a1 = Store(company_id=comp_a.id, name="Alpha Store 1", code="A1")
    db_session.add_all([user_a_admin, user_a_staff, store_a1])
    db_session.flush()

    img_a1_id, storage_key_a1 = create_test_image_file(storage_dir, comp_a.id, store_a1.id)
    image_a1 = Image(
        id=img_a1_id,
        company_id=comp_a.id,
        store_id=store_a1.id,
        uploaded_by=user_a_admin.id,
        original_filename="price_tag_a1.jpg",
        storage_key=storage_key_a1,
        mime_type="image/jpeg",
        file_size=1024,
        width=400,
        height=300,
        checksum="dummy_checksum_a1",
        status=ImageStatus.READY,
        quality_score=90,
        quality_flags=[]
    )
    db_session.add(image_a1)

    # Company B
    comp_b = Company(name="Beta Corp", slug="beta-corp")
    db_session.add(comp_b)
    db_session.flush()

    user_b_admin = User(
        company_id=comp_b.id,
        email="admin@beta.com",
        password_hash=hash_password("password123"),
        full_name="Beta Admin",
        role=UserRole.ADMIN
    )
    store_b1 = Store(company_id=comp_b.id, name="Beta Store 1", code="B1")
    db_session.add_all([user_b_admin, store_b1])
    db_session.flush()

    img_b1_id, storage_key_b1 = create_test_image_file(storage_dir, comp_b.id, store_b1.id)
    image_b1 = Image(
        id=img_b1_id,
        company_id=comp_b.id,
        store_id=store_b1.id,
        uploaded_by=user_b_admin.id,
        original_filename="price_tag_b1.jpg",
        storage_key=storage_key_b1,
        mime_type="image/jpeg",
        file_size=1024,
        width=400,
        height=300,
        checksum="dummy_checksum_b1",
        status=ImageStatus.READY,
        quality_score=90,
        quality_flags=[]
    )
    db_session.add(image_b1)
    db_session.commit()

    token_a_admin = create_access_token(data={"sub": str(user_a_admin.id), "company_id": str(comp_a.id), "role": UserRole.ADMIN})
    token_a_staff = create_access_token(data={"sub": str(user_a_staff.id), "company_id": str(comp_a.id), "role": UserRole.STAFF})
    token_b_admin = create_access_token(data={"sub": str(user_b_admin.id), "company_id": str(comp_b.id), "role": UserRole.ADMIN})

    return {
        "comp_a": comp_a,
        "comp_b": comp_b,
        "store_a1": store_a1,
        "store_b1": store_b1,
        "image_a1": image_a1,
        "image_b1": image_b1,
        "token_a_admin": token_a_admin,
        "token_a_staff": token_a_staff,
        "token_b_admin": token_b_admin,
        "storage_dir": storage_dir
    }


def test_analyze_ocr_unauthenticated(client, setup_tenants_and_images):
    """Test 2: Unauthenticated OCR request is rejected with 401."""
    res = client.post(f"/api/v1/ocr/analyze/{setup_tenants_and_images['image_a1'].id}")
    assert res.status_code == 401


def test_analyze_ocr_missing_or_cross_tenant_image(client, setup_tenants_and_images):
    """Test 4, 5: Missing image or cross-tenant image OCR request returns 404."""
    headers_a = {"Authorization": f"Bearer {setup_tenants_and_images['token_a_admin']}"}

    # Random image ID
    res_rand = client.post(f"/api/v1/ocr/analyze/{uuid.uuid4()}", headers=headers_a)
    assert res_rand.status_code == 404

    # Image B1 belonging to Company B
    res_cross = client.post(f"/api/v1/ocr/analyze/{setup_tenants_and_images['image_b1'].id}", headers=headers_a)
    assert res_cross.status_code == 404


@patch("app.api.v1.ocr.storage_provider")
@patch("app.api.v1.ocr.ocr_service")
def test_successful_ocr_workflow_and_persistence(mock_ocr, mock_storage, client, setup_tenants_and_images):
    """Test 1, 3, 8, 9, 11, 12, 13, 14: Authenticated valid OCR creates AnalysisRun, runs engine, stores recognized text with confidence & bbox."""
    data_ctx = setup_tenants_and_images
    headers_a = {"Authorization": f"Bearer {data_ctx['token_a_admin']}"}

    mock_storage.base_dir = data_ctx["storage_dir"]

    # Mock OCR service output
    mock_ocr.extract_text.return_value = OCREvidence(
        image_width=400,
        image_height=300,
        total_regions=2,
        regions=[
            OCRResultItem(text="  SPECIAL OFFER  ", normalized_text="SPECIAL OFFER", confidence=0.96, line_order=1, bbox=BoundingBox(x_min=10, y_min=20, x_max=150, y_max=50)),
            OCRResultItem(text="$4.99", normalized_text="$4.99", confidence=0.91, line_order=2, bbox=BoundingBox(x_min=10, y_min=60, x_max=80, y_max=90))
        ]
    )

    image_id = data_ctx["image_a1"].id
    response = client.post(f"/api/v1/ocr/analyze/{image_id}", headers=headers_a)

    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status"] == "COMPLETED"
    assert res_data["analysis_type"] == "OCR"
    assert len(res_data["ocr_results"]) == 2

    item0 = res_data["ocr_results"][0]
    assert item0["text"] == "  SPECIAL OFFER  "
    assert item0["normalized_text"] == "SPECIAL OFFER"
    assert item0["confidence"] == 0.96
    assert item0["line_order"] == 1
    assert item0["x_min"] == 10.0

    # Test Duplicate Analysis Reuse Strategy (Test 18)
    res_reuse = client.post(f"/api/v1/ocr/analyze/{image_id}", headers=headers_a)
    assert res_reuse.status_code == 201
    assert res_reuse.json()["id"] == res_data["id"]  # Returns same completed run
    assert mock_ocr.extract_text.call_count == 1  # OCR called only once


@patch("app.api.v1.ocr.storage_provider")
@patch("app.api.v1.ocr.ocr_service")
def test_failed_ocr_analysis_run_error_handling(mock_ocr, mock_storage, client, setup_tenants_and_images):
    """Test 10, 20: OCR execution failure marks AnalysisRun as FAILED and records error message."""
    data_ctx = setup_tenants_and_images
    headers_a = {"Authorization": f"Bearer {data_ctx['token_a_admin']}"}

    mock_storage.base_dir = data_ctx["storage_dir"]
    mock_ocr.extract_text.side_effect = OCRInferenceError("PaddleOCR execution failed")

    image_id = data_ctx["image_a1"].id
    response = client.post(f"/api/v1/ocr/analyze/{image_id}", headers=headers_a)

    assert response.status_code == 201
    res_data = response.json()
    assert res_data["status"] == "FAILED"
    assert "PaddleOCR execution failed" in res_data["error_message"]


@patch("app.api.v1.ocr.storage_provider")
@patch("app.api.v1.ocr.ocr_service")
def test_ocr_retrieval_summary_and_tenant_isolation(mock_ocr, mock_storage, client, setup_tenants_and_images):
    """Test 15, 16, 17, 23: Retrieval APIs (detail, image runs, summary) and tenant isolation."""
    data_ctx = setup_tenants_and_images
    headers_a_admin = {"Authorization": f"Bearer {data_ctx['token_a_admin']}"}
    headers_a_staff = {"Authorization": f"Bearer {data_ctx['token_a_staff']}"}
    headers_b_admin = {"Authorization": f"Bearer {data_ctx['token_b_admin']}"}

    mock_storage.base_dir = data_ctx["storage_dir"]
    mock_ocr.extract_text.return_value = OCREvidence(
        image_width=400,
        image_height=300,
        total_regions=1,
        regions=[
            OCRResultItem(text="ORGANIC MILK", normalized_text="ORGANIC MILK", confidence=0.98, line_order=1, bbox=BoundingBox(x_min=0, y_min=0, x_max=100, y_max=30))
        ]
    )

    img_id = data_ctx["image_a1"].id

    # STAFF role runs analysis
    res_staff_run = client.post(f"/api/v1/ocr/analyze/{img_id}", headers=headers_a_staff)
    assert res_staff_run.status_code == 201
    run_id = res_staff_run.json()["id"]

    # Retrieve run detail
    res_detail = client.get(f"/api/v1/ocr/{run_id}", headers=headers_a_staff)
    assert res_detail.status_code == 200
    assert res_detail.json()["id"] == run_id

    # Retrieve image analysis runs list
    res_list = client.get(f"/api/v1/ocr/image/{img_id}", headers=headers_a_admin)
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # Retrieve run summary
    res_summary = client.get(f"/api/v1/ocr/{run_id}/summary", headers=headers_a_admin)
    assert res_summary.status_code == 200
    summary_data = res_summary.json()
    assert summary_data["total_regions"] == 1
    assert summary_data["extracted_text_sample"] == ["ORGANIC MILK"]

    # Cross-tenant access attempt by Company B -> 404 Not Found
    res_cross_detail = client.get(f"/api/v1/ocr/{run_id}", headers=headers_b_admin)
    assert res_cross_detail.status_code == 404

    res_cross_summary = client.get(f"/api/v1/ocr/{run_id}/summary", headers=headers_b_admin)
    assert res_cross_summary.status_code == 404
