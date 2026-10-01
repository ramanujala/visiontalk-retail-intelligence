"""Pytest Suite for Phase 8 Compliance Rules CRUD & Retail Compliance Rules Engine."""

import uuid
from datetime import datetime, timezone
import pytest

from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.compliance_rule import ComplianceRule, ComplianceFinding, RuleType, RuleSeverity, FindingStatus
from app.models.expected_product import ExpectedProduct
from app.models.analysis import AnalysisRun, Detection, OCRResult, AnalysisRunStatus, AnalysisType
from app.core.security import hash_password, create_access_token
from app.services.compliance_engine import ComplianceEngine


# --- 1. COMPLIANCE RULE CRUD & TENANT ISOLATION TESTS ---

def test_create_compliance_rule(client, db_session):
    comp = Company(name="Rules Corp", slug="rules-corp")
    db_session.add(comp)
    db_session.flush()

    admin = User(
        company_id=comp.id,
        email="admin@rules.com",
        password_hash=hash_password("pass"),
        full_name="Admin R",
        role=UserRole.ADMIN
    )
    db_session.add(admin)
    db_session.commit()

    token = create_access_token(data={"sub": str(admin.id), "company_id": str(comp.id), "role": UserRole.ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "name": "Coca Cola Required Rule",
        "description": "Ensures Coca Cola bottle is present on shelf",
        "rule_type": "PRODUCT_REQUIRED",
        "severity": "HIGH",
        "configuration": {"product_name": "bottle"},
        "is_active": True
    }

    res = client.post("/api/v1/compliance-rules", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Coca Cola Required Rule"
    assert data["severity"] == "HIGH"


def test_compliance_rule_tenant_isolation(client, db_session):
    # Tenant A
    comp_a = Company(name="Tenant A Rules", slug="tenant-a-rules")
    db_session.add(comp_a)
    db_session.flush()

    user_a = User(company_id=comp_a.id, email="usera@ta.com", password_hash=hash_password("p"), full_name="A", role=UserRole.ADMIN)
    db_session.add(user_a)

    # Tenant B
    comp_b = Company(name="Tenant B Rules", slug="tenant-b-rules")
    db_session.add(comp_b)
    db_session.flush()

    user_b = User(company_id=comp_b.id, email="userb@tb.com", password_hash=hash_password("p"), full_name="B", role=UserRole.ADMIN)
    db_session.add(user_b)
    db_session.flush()

    rule_b = ComplianceRule(
        company_id=comp_b.id,
        created_by=user_b.id,
        name="Rule B",
        rule_type="PRODUCT_REQUIRED",
        severity="MEDIUM",
        configuration={"product_code": "SKU-B"}
    )
    db_session.add(rule_b)
    db_session.commit()

    token_a = create_access_token(data={"sub": str(user_a.id), "company_id": str(comp_a.id), "role": UserRole.ADMIN})
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User A tries to view Tenant B rule -> 404
    res = client.get(f"/api/v1/compliance-rules/{rule_b.id}", headers=headers_a)
    assert res.status_code == 404
    assert res.json()["error"]["message"] == "Compliance rule not found."


# --- 2. COMPLIANCE ENGINE EVALUATION TESTS ---

def test_compliance_engine_evaluation_pass_and_fail(db_session):
    comp = Company(name="Eval Corp", slug="eval-corp")
    db_session.add(comp)
    db_session.flush()

    user = User(company_id=comp.id, email="user@eval.com", password_hash=hash_password("p"), full_name="U", role=UserRole.ADMIN)
    store = Store(company_id=comp.id, name="Store 1", code="S1")
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
        checksum="dummy_checksum_eval",
        status=ImageStatus.READY
    )
    db_session.add(img)
    db_session.flush()

    # Rule 1: PRODUCT_REQUIRED (bottle) -> PASS (since 2 bottles detected)
    # Rule 2: PRODUCT_QUANTITY (bottle min 5) -> FAIL (since 2 observed < 5)
    # Rule 3: OCR_REQUIRED ("ORGANIC") -> PASS (since OCR recognized ORGANIC)
    rule1 = ComplianceRule(company_id=comp.id, created_by=user.id, name="Bottle Required", rule_type=RuleType.PRODUCT_REQUIRED, severity=RuleSeverity.HIGH, configuration={"product_name": "bottle"})
    rule2 = ComplianceRule(company_id=comp.id, created_by=user.id, name="Bottle Min Qty 5", rule_type=RuleType.PRODUCT_QUANTITY, severity=RuleSeverity.CRITICAL, configuration={"product_name": "bottle", "minimum_quantity": 5})
    rule3 = ComplianceRule(company_id=comp.id, created_by=user.id, name="Organic Text Required", rule_type=RuleType.OCR_REQUIRED, severity=RuleSeverity.MEDIUM, configuration={"required_text": "ORGANIC"})
    db_session.add_all([rule1, rule2, rule3])

    # Perception outputs
    det_run = AnalysisRun(company_id=comp.id, image_id=img.id, initiated_by=user.id, analysis_type=AnalysisType.OBJECT_DETECTION, status=AnalysisRunStatus.COMPLETED, completed_at=datetime.now(timezone.utc))
    db_session.add(det_run)
    db_session.flush()

    d1 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=0, class_name="bottle", confidence=0.95, x_min=10, y_min=10, x_max=50, y_max=50)
    d2 = Detection(analysis_run_id=det_run.id, company_id=comp.id, class_id=0, class_name="bottle", confidence=0.92, x_min=60, y_min=10, x_max=100, y_max=50)
    db_session.add_all([d1, d2])

    ocr_run = AnalysisRun(company_id=comp.id, image_id=img.id, initiated_by=user.id, analysis_type=AnalysisType.OCR, status=AnalysisRunStatus.COMPLETED, completed_at=datetime.now(timezone.utc))
    db_session.add(ocr_run)
    db_session.flush()

    o1 = OCRResult(analysis_run_id=ocr_run.id, company_id=comp.id, text="ORGANIC MILK 1L", normalized_text="ORGANIC MILK 1L", confidence=0.98, x_min=10, y_min=60, x_max=100, y_max=80)
    db_session.add(o1)
    db_session.commit()

    # Evaluate Compliance Engine
    engine = ComplianceEngine(db_session)
    run = engine.evaluate_rules(image_id=img.id, company_id=comp.id, initiated_by_user_id=user.id)

    assert run.status == AnalysisRunStatus.COMPLETED
    findings = run.compliance_findings
    assert len(findings) == 3

    statuses = {f.rule_id: f.status for f in findings}
    assert statuses[rule1.id] == FindingStatus.PASS
    assert statuses[rule2.id] == FindingStatus.FAIL
    assert statuses[rule3.id] == FindingStatus.PASS


def test_compliance_api_workflow(client, db_session):
    comp = Company(name="API Compliance", slug="api-compliance")
    db_session.add(comp)
    db_session.flush()

    user = User(company_id=comp.id, email="admin@apicomp.com", password_hash=hash_password("p"), full_name="Admin Comp", role=UserRole.ADMIN)
    store = Store(company_id=comp.id, name="Store C", code="SC")
    db_session.add_all([user, store])
    db_session.flush()

    img = Image(company_id=comp.id, store_id=store.id, uploaded_by=user.id, original_filename="shelf_comp.jpg", storage_key=f"uploads/shelf_comp.jpg", mime_type="image/jpeg", file_size=1024, width=800, height=600, checksum="checksum_comp", status=ImageStatus.READY)
    db_session.add(img)
    db_session.commit()

    token = create_access_token(data={"sub": str(user.id), "company_id": str(comp.id), "role": UserRole.ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    # Execute Compliance Analysis API
    res = client.post(f"/api/v1/compliance/analyze/{img.id}", headers=headers)
    assert res.status_code == 201
    run_id = res.json()["id"]

    # Get Summary API
    res_sum = client.get(f"/api/v1/compliance/image/{img.id}/summary", headers=headers)
    assert res_sum.status_code == 200
    assert res_sum.json()["image_id"] == str(img.id)
