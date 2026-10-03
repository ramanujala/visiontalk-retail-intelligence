import pytest
from fastapi import status
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.models.conversation import Conversation, Message, MessageRole
from app.core.security import hash_password, create_access_token


@pytest.fixture
def conversation_test_setup(db_session):
    company_a = Company(name="Conv Co A", slug="conv-co-a")
    company_b = Company(name="Conv Co B", slug="conv-co-b")
    db_session.add_all([company_a, company_b])
    db_session.flush()

    user_a = User(
        company_id=company_a.id,
        email="user@conva.com",
        password_hash=hash_password("password123"),
        full_name="User A",
        role=UserRole.ADMIN
    )
    user_b = User(
        company_id=company_b.id,
        email="user@convb.com",
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
        storage_key="conv/shelf_a.jpg",
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
        storage_key="conv/shelf_b.jpg",
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
    token_b = create_access_token(data={"sub": str(user_b.id), "company_id": str(company_b.id), "role": user_b.role})

    return {
        "company_a": company_a,
        "company_b": company_b,
        "user_a": user_a,
        "user_b": user_b,
        "image_a": image_a,
        "image_b": image_b,
        "headers_a": {"Authorization": f"Bearer {token_a}"},
        "headers_b": {"Authorization": f"Bearer {token_b}"}
    }


def test_create_and_list_conversations(client, conversation_test_setup):
    """Test creating and listing conversations for Company A."""
    response = client.post(
        "/api/v1/conversations",
        json={"title": "Shelf Audit Session #1"},
        headers=conversation_test_setup["headers_a"]
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Shelf Audit Session #1"
    assert data["company_id"] == str(conversation_test_setup["company_a"].id)

    # List conversations
    list_res = client.get("/api/v1/conversations", headers=conversation_test_setup["headers_a"])
    assert list_res.status_code == status.HTTP_200_OK
    conversations = list_res.json()
    assert len(conversations) == 1
    assert conversations[0]["id"] == data["id"]


def test_post_message_and_router_execution(client, conversation_test_setup):
    """Test posting a user message triggers QuestionRouter and generates Assistant message."""
    conv_res = client.post(
        "/api/v1/conversations",
        json={"title": "Product Count Inquiry"},
        headers=conversation_test_setup["headers_a"]
    )
    conv_id = conv_res.json()["id"]

    msg_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={
            "content": "How many products are visible on shelf?",
            "image_id": str(conversation_test_setup["image_a"].id)
        },
        headers=conversation_test_setup["headers_a"]
    )
    assert msg_res.status_code == status.HTTP_201_CREATED
    msg_data = msg_res.json()
    assert msg_data["role"] == "ASSISTANT"
    assert msg_data["intent"] == "COUNT"
    assert "Observed a total of" in msg_data["content"]

    # Verify Detail includes chronologically ordered messages (USER then ASSISTANT)
    detail_res = client.get(f"/api/v1/conversations/{conv_id}", headers=conversation_test_setup["headers_a"])
    detail_data = detail_res.json()
    assert len(detail_data["messages"]) == 2
    assert detail_data["messages"][0]["role"] == "USER"
    assert detail_data["messages"][1]["role"] == "ASSISTANT"


def test_conversation_tenant_isolation(client, conversation_test_setup):
    """Test Company B cannot access Company A's conversation session."""
    conv_res = client.post(
        "/api/v1/conversations",
        json={"title": "Private Session A"},
        headers=conversation_test_setup["headers_a"]
    )
    conv_id = conv_res.json()["id"]

    # User B attempts to view Session A
    get_res = client.get(f"/api/v1/conversations/{conv_id}", headers=conversation_test_setup["headers_b"])
    assert get_res.status_code == status.HTTP_404_NOT_FOUND

    # User B attempts to post message to Session A
    post_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={"content": "Unauthorized message"},
        headers=conversation_test_setup["headers_b"]
    )
    assert post_res.status_code == status.HTTP_404_NOT_FOUND


def test_cross_tenant_image_message_rejected(client, conversation_test_setup):
    """Test User A cannot attach Company B's image to a conversation message."""
    conv_res = client.post(
        "/api/v1/conversations",
        json={"title": "Session A"},
        headers=conversation_test_setup["headers_a"]
    )
    conv_id = conv_res.json()["id"]

    msg_res = client.post(
        f"/api/v1/conversations/{conv_id}/messages",
        json={
            "content": "Analyze Company B image",
            "image_id": str(conversation_test_setup["image_b"].id)
        },
        headers=conversation_test_setup["headers_a"]
    )
    assert msg_res.status_code == status.HTTP_404_NOT_FOUND
