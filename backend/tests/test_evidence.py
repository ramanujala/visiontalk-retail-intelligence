"""Unit and Integration Test Suite for Phase 6 Evidence Engine & Spatial Utilities."""

import uuid
from datetime import datetime, timezone
import pytest
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.analysis import AnalysisRun, Detection, OCRResult, AnalysisRunStatus, AnalysisType
from app.core.security import hash_password, create_access_token
from app.services.evidence.spatial import (
    BoundingBox,
    calculate_intersection_area,
    calculate_iou,
    calculate_overlap_ratio,
    calculate_containment,
    calculate_center_distance,
    classify_spatial_relationship
)
from app.services.evidence.engine import EvidenceEngine
from app.services.evidence.exceptions import EvidenceNotFoundError


# --- 1. SPATIAL CALCULATIONS TESTS ---

def test_spatial_utilities_intersection_and_iou():
    box1 = BoundingBox(x_min=10.0, y_min=10.0, x_max=50.0, y_max=50.0) # 40x40 = 1600
    box2 = BoundingBox(x_min=30.0, y_min=30.0, x_max=70.0, y_max=70.0) # 40x40 = 1600, inter = 20x20 = 400

    inter_area = calculate_intersection_area(box1, box2)
    assert inter_area == 400.0

    # Union = 1600 + 1600 - 400 = 2800. IoU = 400 / 2800 = 0.1429
    iou = calculate_iou(box1, box2)
    assert iou == 0.1429


def test_spatial_utilities_containment_and_distance():
    outer = BoundingBox(x_min=0.0, y_min=0.0, x_max=100.0, y_max=100.0)
    inner = BoundingBox(x_min=20.0, y_min=20.0, x_max=40.0, y_max=40.0)
    outside = BoundingBox(x_min=200.0, y_min=200.0, x_max=250.0, y_max=250.0)

    assert calculate_containment(inner, outer) is True
    assert calculate_containment(outside, outer) is False

    # Outer center = (50, 50), Inner center = (30, 30). dx=20, dy=20, dist = sqrt(800) = 28.2843
    dist = calculate_center_distance(inner, outer)
    assert dist == 28.2843


def test_classify_spatial_relationship():
    det = BoundingBox(x_min=100.0, y_min=100.0, x_max=300.0, y_max=300.0)
    ocr = BoundingBox(x_min=120.0, y_min=120.0, x_max=200.0, y_max=150.0)

    metrics = classify_spatial_relationship(det, ocr)
    assert metrics["is_contained"] == 1.0
    assert metrics["ocr_overlap_ratio"] == 1.0
    assert metrics["center_distance"] > 0.0


# --- 2. EVIDENCE ENGINE INTEGRATION TESTS ---

def test_evidence_engine_generation(db_session):
    comp_a = Company(name="Test Company A", slug="test-company-a")
    db_session.add(comp_a)
    db_session.flush()

    user_a = User(
        company_id=comp_a.id,
        email="usera@testa.com",
        password_hash=hash_password("password"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    store_a = Store(company_id=comp_a.id, name="Store A", code="STORE-A")
    db_session.add_all([user_a, store_a])
    db_session.flush()

    # Setup test image
    img = Image(
        company_id=comp_a.id,
        store_id=store_a.id,
        uploaded_by=user_a.id,
        original_filename="shelf_test.jpg",
        storage_key=f"uploads/{comp_a.id}/{store_a.id}/shelf_test.jpg",
        file_size=1024,
        mime_type="image/jpeg",
        width=1000,
        height=1000,
        checksum="dummy_checksum_a",
        status=ImageStatus.READY
    )
    db_session.add(img)
    db_session.commit()

    # Setup Object Detection Run
    det_run = AnalysisRun(
        company_id=comp_a.id,
        image_id=img.id,
        initiated_by=user_a.id,
        analysis_type=AnalysisType.OBJECT_DETECTION,
        status=AnalysisRunStatus.COMPLETED,
        model_name="YOLOv8",
        model_version="yolov8n",
        completed_at=datetime.now(timezone.utc)
    )
    db_session.add(det_run)
    db_session.commit()

    det = Detection(
        analysis_run_id=det_run.id,
        company_id=comp_a.id,
        class_id=0,
        class_name="bottle",
        confidence=0.92,
        x_min=100.0,
        y_min=100.0,
        x_max=300.0,
        y_max=500.0
    )
    db_session.add(det)

    # Setup OCR Run
    ocr_run = AnalysisRun(
        company_id=comp_a.id,
        image_id=img.id,
        initiated_by=user_a.id,
        analysis_type=AnalysisType.OCR,
        status=AnalysisRunStatus.COMPLETED,
        model_name="PaddleOCR",
        model_version="paddleocr-en",
        completed_at=datetime.now(timezone.utc)
    )
    db_session.add(ocr_run)
    db_session.commit()

    ocr = OCRResult(
        analysis_run_id=ocr_run.id,
        company_id=comp_a.id,
        text="500 ml",
        normalized_text="500 ml",
        confidence=0.98,
        line_order=1,
        x_min=120.0,
        y_min=450.0,
        x_max=250.0,
        y_max=480.0
    )
    db_session.add(ocr)
    db_session.commit()

    # Run Evidence Engine
    engine = EvidenceEngine(db_session)
    evidence = engine.generate_canonical_evidence(image_id=img.id, company_id=comp_a.id)

    assert evidence.image_id == img.id
    assert evidence.company_id == comp_a.id
    assert evidence.evidence_version == "1.0"
    assert len(evidence.detections) == 1
    assert len(evidence.ocr_results) == 1
    assert evidence.metadata.total_associations == 1

    det_item = evidence.detections[0]
    assert det_item.class_name == "bottle"
    assert ocr.id in det_item.related_ocr_ids
    assert len(det_item.spatial_relationships) == 1
    assert det_item.spatial_relationships[0]["ocr_text"] == "500 ml"


def test_evidence_engine_cross_tenant_isolation(client, db_session):
    # Company A
    comp_a = Company(name="Tenant A Corp", slug="tenant-a-corp")
    db_session.add(comp_a)
    db_session.flush()

    user_a = User(
        company_id=comp_a.id,
        email="usera@tenanta.com",
        password_hash=hash_password("password"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    db_session.add(user_a)
    db_session.commit()

    token_a = create_access_token(data={"sub": str(user_a.id), "company_id": str(comp_a.id), "role": UserRole.ADMIN})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Company B
    comp_b = Company(name="Tenant B Corp", slug="tenant-b-corp")
    db_session.add(comp_b)
    db_session.flush()

    user_b = User(
        company_id=comp_b.id,
        email="userb@tenantb.com",
        password_hash=hash_password("password"),
        full_name="User B",
        role=UserRole.ADMIN
    )
    store_b = Store(company_id=comp_b.id, name="Store B", code="STORE-B")
    db_session.add_all([user_b, store_b])
    db_session.flush()

    img_b = Image(
        company_id=comp_b.id,
        store_id=store_b.id,
        uploaded_by=user_b.id,
        original_filename="tenant_b.jpg",
        storage_key="uploads/tenant_b.jpg",
        file_size=500,
        mime_type="image/jpeg",
        width=500,
        height=500,
        checksum="dummy_checksum_b",
        status=ImageStatus.READY
    )
    db_session.add(img_b)
    db_session.commit()

    # User A attempts to generate evidence for Image B -> expect 404
    response = client.post(f"/api/v1/evidence/generate/{img_b.id}", headers=headers_a)
    assert response.status_code == 404
    assert response.json()["error"]["message"] == "Image not found."
