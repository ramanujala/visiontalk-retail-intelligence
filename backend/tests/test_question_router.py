import pytest
from fastapi import status
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.core.security import hash_password, create_access_token
from app.schemas.question_router import QuestionIntent, QuestionRouteRequest
from app.services.intent_classifier import IntentClassifier
from app.services.question_router import QuestionRouter


@pytest.fixture
def question_router_setup(db_session):
    company_a = Company(name="Router Co A", slug="router-co-a")
    company_b = Company(name="Router Co B", slug="router-co-b")
    db_session.add_all([company_a, company_b])
    db_session.flush()

    user_a = User(
        company_id=company_a.id,
        email="user@routera.com",
        password_hash=hash_password("password123"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    user_b = User(
        company_id=company_b.id,
        email="user@routerb.com",
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
        storage_key="router/shelf_a.jpg",
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
        storage_key="router/shelf_b.jpg",
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


def test_intent_classifier_count_queries():
    classifier = IntentClassifier()
    intent, route, conf, reason, target = classifier.classify("How many products are visible on shelf?")
    assert intent == QuestionIntent.COUNT
    assert route == "detections"
    assert conf >= 0.90


def test_intent_classifier_availability_queries():
    classifier = IntentClassifier()
    intent, route, conf, reason, target = classifier.classify("Is Coca Cola available on the top shelf?")
    assert intent == QuestionIntent.AVAILABILITY
    assert route == "availability"


def test_intent_classifier_expected_vs_actual_queries():
    classifier = IntentClassifier()
    intent, route, conf, reason, target = classifier.classify("Which expected products are missing?")
    assert intent == QuestionIntent.EXPECTED_VS_ACTUAL
    assert route == "expected_vs_actual"


def test_intent_classifier_compliance_queries():
    classifier = IntentClassifier()
    intent, route, conf, reason, target = classifier.classify("Is this shelf compliant with store rules?")
    assert intent == QuestionIntent.COMPLIANCE
    assert route == "compliance"


def test_intent_classifier_case_and_whitespace_normalization():
    classifier = IntentClassifier()
    res1 = classifier.classify("   HOW   MANY   PRODUCTS ARE  VISIBLE?  ")
    res2 = classifier.classify("how many products are visible?")
    assert res1[0] == res2[0]
    assert res1[1] == res2[1]


def test_question_router_api_success(client, question_router_setup):
    payload = {
        "question": "Which products are missing from the shelf?",
        "image_id": str(question_router_setup["image_a"].id)
    }
    response = client.post(
        "/api/v1/questions/route",
        json=payload,
        headers=question_router_setup["headers_a"]
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["intent"] == "EXPECTED_VS_ACTUAL"
    assert data["route"] == "expected_vs_actual"
    assert data["confidence"] > 0.80


def test_question_router_tenant_isolation(client, question_router_setup):
    """Company A cannot pass Company B image_id for question routing."""
    payload = {
        "question": "How many items are present?",
        "image_id": str(question_router_setup["image_b"].id)
    }
    response = client.post(
        "/api/v1/questions/route",
        json=payload,
        headers=question_router_setup["headers_a"]
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
