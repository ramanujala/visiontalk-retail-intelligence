"""Pytest Suite for Phase 7 Expected Products CRUD & Expected vs Actual Reasoning Engine."""

import uuid
from datetime import datetime, timezone
import pytest
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.expected_product import ExpectedProduct
from app.models.analysis import (
    AnalysisRun,
    Detection,
    OCRResult,
    AnalysisRunStatus,
    AnalysisType,
    ExpectedActualItemStatus,
    ExpectedActualIssueType,
    ExpectedActualIssueSeverity
)
from app.core.security import hash_password, create_access_token
from app.services.expected_actual import ExpectedActualEngine


# --- 1. EXPECTED PRODUCTS CRUD & VALIDATION TESTS ---

def test_create_expected_product_success(client, db_session):
    comp = Company(name="Corp A", slug="corp-a")
    db_session.add(comp)
    db_session.flush()

    admin = User(
        company_id=comp.id,
        email="admin@corpa.com",
        password_hash=hash_password("pass"),
        full_name="Admin A",
        role=UserRole.ADMIN
    )
    store = Store(company_id=comp.id, name="Store 1", code="S1")
    db_session.add_all([admin, store])
    db_session.commit()

    token = create_access_token(data={"sub": str(admin.id), "company_id": str(comp.id), "role": UserRole.ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "store_id": str(store.id),
        "product_name": "Organic Milk 1L",
        "product_code": "MILK-01",
        "expected_quantity": 4,
        "expected_min_quantity": 2,
        "expected_max_quantity": 8,
        "is_active": True
    }

    res = client.post("/api/v1/expected-products", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["product_code"] == "MILK-01"
    assert data["expected_quantity"] == 4


def test_create_expected_product_validation_failure(client, db_session):
    comp = Company(name="Corp B", slug="corp-b")
    db_session.add(comp)
    db_session.flush()

    admin = User(
        company_id=comp.id,
        email="admin@corpb.com",
        password_hash=hash_password("pass"),
        full_name="Admin B",
        role=UserRole.ADMIN
    )
    store = Store(company_id=comp.id, name="Store B", code="SB")
    db_session.add_all([admin, store])
    db_session.commit()

    token = create_access_token(data={"sub": str(admin.id), "company_id": str(comp.id), "role": UserRole.ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    # Invalid: max < min
    payload = {
        "store_id": str(store.id),
        "product_name": "Soda",
        "product_code": "SODA-01",
        "expected_quantity": 5,
        "expected_min_quantity": 10,
        "expected_max_quantity": 2,
        "is_active": True
    }

    res = client.post("/api/v1/expected-products", json=payload, headers=headers)
    assert res.status_code == 422


def test_expected_product_cross_tenant_isolation(client, db_session):
    # Tenant A
    comp_a = Company(name="Corp Tenant A", slug="corp-tenant-a")
    db_session.add(comp_a)
    db_session.flush()

    user_a = User(
        company_id=comp_a.id,
        email="usera@tenanta.com",
        password_hash=hash_password("pass"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    store_a = Store(company_id=comp_a.id, name="Store A", code="SA")
    db_session.add_all([user_a, store_a])

    # Tenant B
    comp_b = Company(name="Corp Tenant B", slug="corp-tenant-b")
    db_session.add(comp_b)
    db_session.flush()

    store_b = Store(company_id=comp_b.id, name="Store B", code="SB")
    db_session.add(store_b)
    db_session.flush()

    exp_b = ExpectedProduct(
        company_id=comp_b.id,
        store_id=store_b.id,
        product_name="Tenant B Item",
        product_code="ITEM-B",
        expected_quantity=2,
        expected_min_quantity=1,
        expected_max_quantity=5
    )
    db_session.add(exp_b)
    db_session.commit()

    token_a = create_access_token(data={"sub": str(user_a.id), "company_id": str(comp_a.id), "role": UserRole.ADMIN})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A tries to get Tenant B expected product -> 404
    res = client.get(f"/api/v1/expected-products/{exp_b.id}", headers=headers_a)
    assert res.status_code == 404
    assert res.json()["error"]["message"] == "Expected product not found."


# --- 2. EXPECTED VS ACTUAL REASONING ENGINE TESTS ---

def test_expected_actual_engine_comparison_statuses(db_session):
    comp = Company(name="Reasoning Corp", slug="reasoning-corp")
    db_session.add(comp)
    db_session.flush()

    user = User(
        company_id=comp.id,
        email="user@reasoning.com",
        password_hash=hash_password("pass"),
        full_name="User R",
        role=UserRole.ADMIN
    )
    store = Store(company_id=comp.id, name="Reasoning Store", code="RS1")
    db_session.add_all([user, store])
    db_session.flush()

    img = Image(
        company_id=comp.id,
        store_id=store.id,
        uploaded_by=user.id,
        original_filename="shelf.jpg",
        storage_key=f"uploads/{comp.id}/{store.id}/shelf.jpg",
        mime_type="image/jpeg",
        file_size=1024,
        width=800,
        height=600,
        checksum="dummy_checksum_r",
        status=ImageStatus.READY
    )
    db_session.add(img)
    db_session.flush()

    # Configure 3 expected products:
    # 1. BOTTLE -> Expected: 2, min: 1, max: 3. We will observe 2 -> OBSERVED
    # 2. CAN -> Expected: 5, min: 3, max: 10. We will observe 1 -> LOW_STOCK
    # 3. JUICE -> Expected: 4, min: 2, max: 6. We will observe 0 -> MISSING
    exp1 = ExpectedProduct(company_id=comp.id, store_id=store.id, product_name="Bottle Water", product_code="BOTTLE", expected_quantity=2, expected_min_quantity=1, expected_max_quantity=3)
    exp2 = ExpectedProduct(company_id=comp.id, store_id=store.id, product_name="Soda Can", product_code="CAN", expected_quantity=5, expected_min_quantity=3, expected_max_quantity=10)
    exp3 = ExpectedProduct(company_id=comp.id, store_id=store.id, product_name="Juice Box", product_code="JUICE", expected_quantity=4, expected_min_quantity=2, expected_max_quantity=6)
    db_session.add_all([exp1, exp2, exp3])

    # Setup Object Detection Run (Observes: 2 BOTTLEs, 1 CAN, 1 UNEXPECTED CHIPS)
    det_run = AnalysisRun(
        company_id=comp.id,
        image_id=img.id,
        initiated_by=user.id,
        analysis_type=AnalysisType.OBJECT_DETECTION,
        status=AnalysisRunStatus.COMPLETED,
        model_name="YOLOv8",
        model_version="yolov8n",
        completed_at=datetime.now(timezone.utc)
    )
    db_session.add(det_run)
    db_session.flush()

    d1 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=0, class_name="bottle", confidence=0.9, x_min=10, y_min=10, x_max=50, y_max=50)
    d2 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=0, class_name="bottle", confidence=0.9, x_min=60, y_min=10, x_max=100, y_max=50)
    d3 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=1, class_name="can", confidence=0.85, x_min=10, y_min=60, x_max=50, y_max=100)
    d4 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=2, class_name="chips", confidence=0.8, x_min=100, y_min=100, x_max=150, y_max=150)
    db_session.add_all([d1, d2, d3, d4])
    db_session.commit()

    # Run Engine
    engine = ExpectedActualEngine(db_session)
    run = engine.analyze(image_id=img.id, company_id=comp.id, initiated_by_user_id=user.id)

    assert run.status == AnalysisRunStatus.COMPLETED
    assert len(run.expected_actual_items) == 4
    assert len(run.expected_actual_issues) == 3

    statuses = {item.product_code: item.status for item in run.expected_actual_items}
    assert statuses["BOTTLE"] == ExpectedActualItemStatus.OBSERVED
    assert statuses["CAN"] == ExpectedActualItemStatus.LOW_STOCK
    assert statuses["JUICE"] == ExpectedActualItemStatus.MISSING
    assert statuses["CHIPS"] == ExpectedActualItemStatus.UNEXPECTED


def test_expected_actual_api_workflow(client, db_session):
    comp = Company(name="API Corp", slug="api-corp")
    db_session.add(comp)
    db_session.flush()

    user = User(
        company_id=comp.id,
        email="admin@apicorp.com",
        password_hash=hash_password("pass"),
        full_name="Admin API",
        role=UserRole.ADMIN
    )
    store = Store(company_id=comp.id, name="API Store", code="AS1")
    db_session.add_all([user, store])
    db_session.flush()

    img = Image(
        company_id=comp.id,
        store_id=store.id,
        uploaded_by=user.id,
        original_filename="shelf_api.jpg",
        storage_key=f"uploads/{comp.id}/{store.id}/shelf_api.jpg",
        mime_type="image/jpeg",
        file_size=1024,
        width=800,
        height=600,
        checksum="dummy_checksum_api",
        status=ImageStatus.READY
    )
    db_session.add(img)
    db_session.commit()

    token = create_access_token(data={"sub": str(user.id), "company_id": str(comp.id), "role": UserRole.ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    # Execute Analysis API
    res = client.post(f"/api/v1/analysis/expected-vs-actual/{img.id}", headers=headers)
    assert res.status_code == 201
    run_id = res.json()["id"]

    # Get Analysis Detail API
    res_get = client.get(f"/api/v1/analysis/expected-vs-actual/{run_id}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == run_id

    # List Analyses for Image API
    res_list = client.get(f"/api/v1/analysis/expected-vs-actual/image/{img.id}", headers=headers)
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
