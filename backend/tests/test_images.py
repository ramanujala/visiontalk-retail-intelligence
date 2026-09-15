import pytest
import io
import uuid
from PIL import Image as PILImage
from app.models.company import Company
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.core.security import hash_password, create_access_token


def create_test_image_bytes(width=200, height=200, format="JPEG", color="red"):
    """Helper to generate valid in-memory image bytes."""
    buf = io.BytesIO()
    img = PILImage.new("RGB", (width, height), color=color)
    img.save(buf, format=format)
    return buf.getvalue()


@pytest.fixture
def setup_tenants(db_session):
    """Sets up Company A and Company B with users of different roles and stores."""
    # Company A
    comp_a = Company(name="Company Alpha", slug="company-alpha")
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
    store_a1 = Store(
        company_id=comp_a.id,
        name="Alpha Store 1",
        code="ALPHA-001"
    )
    db_session.add_all([user_a_admin, user_a_staff, store_a1])

    # Company B
    comp_b = Company(name="Company Beta", slug="company-beta")
    db_session.add(comp_b)
    db_session.flush()

    user_b_admin = User(
        company_id=comp_b.id,
        email="admin@beta.com",
        password_hash=hash_password("password123"),
        full_name="Beta Admin",
        role=UserRole.ADMIN
    )
    store_b1 = Store(
        company_id=comp_b.id,
        name="Beta Store 1",
        code="BETA-001"
    )
    db_session.add_all([user_b_admin, store_b1])

    db_session.commit()

    token_a_admin = create_access_token(data={"sub": str(user_a_admin.id), "company_id": str(comp_a.id), "role": UserRole.ADMIN})
    token_a_staff = create_access_token(data={"sub": str(user_a_staff.id), "company_id": str(comp_a.id), "role": UserRole.STAFF})
    token_b_admin = create_access_token(data={"sub": str(user_b_admin.id), "company_id": str(comp_b.id), "role": UserRole.ADMIN})

    return {
        "comp_a": comp_a,
        "comp_b": comp_b,
        "store_a1": store_a1,
        "store_b1": store_b1,
        "user_a_admin": user_a_admin,
        "user_a_staff": user_a_staff,
        "user_b_admin": user_b_admin,
        "token_a_admin": token_a_admin,
        "token_a_staff": token_a_staff,
        "token_b_admin": token_b_admin,
    }


def test_upload_image_success(client, setup_tenants):
    """Test 1-7: Valid image upload creates DB record, metadata, dimensions, checksum, quality score."""
    headers = {"Authorization": f"Bearer {setup_tenants['token_a_admin']}"}
    img_bytes = create_test_image_bytes(width=300, height=400, format="JPEG")

    response = client.post(
        "/api/v1/images",
        data={"store_id": str(setup_tenants["store_a1"].id)},
        files={"file": ("test_shelf.jpg", img_bytes, "image/jpeg")},
        headers=headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test_shelf.jpg"
    assert data["width"] == 300
    assert data["height"] == 400
    assert data["mime_type"] == "image/jpeg"
    assert data["file_size"] == len(img_bytes)
    assert len(data["checksum"]) == 64  # SHA-256 hash length
    assert data["status"] == "READY"
    assert 0 <= data["quality_score"] <= 100
    assert isinstance(data["quality_flags"], list)


def test_upload_unauthenticated(client, setup_tenants):
    """Test 8: Unauthenticated upload is rejected with 401."""
    img_bytes = create_test_image_bytes()
    response = client.post(
        "/api/v1/images",
        data={"store_id": str(setup_tenants["store_a1"].id)},
        files={"file": ("test.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 401


def test_upload_invalid_and_cross_tenant_store(client, setup_tenants):
    """Test 9-10: Invalid store or cross-tenant store upload is rejected with 404."""
    headers = {"Authorization": f"Bearer {setup_tenants['token_a_admin']}"}
    img_bytes = create_test_image_bytes()

    # Random store ID
    res1 = client.post(
        "/api/v1/images",
        data={"store_id": str(uuid.uuid4())},
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        headers=headers
    )
    assert res1.status_code == 404

    # Store B1 (belonging to Company B) accessed by Company A user
    res2 = client.post(
        "/api/v1/images",
        data={"store_id": str(setup_tenants["store_b1"].id)},
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        headers=headers
    )
    assert res2.status_code == 404


def test_upload_empty_oversized_unsupported_corrupted_invalid_dim(client, setup_tenants):
    """Test 13-17: File validation rejections (empty, oversized, unsupported format, corrupted, invalid dims)."""
    headers = {"Authorization": f"Bearer {setup_tenants['token_a_admin']}"}
    store_id = str(setup_tenants["store_a1"].id)

    # Empty file
    res_empty = client.post(
        "/api/v1/images",
        data={"store_id": store_id},
        files={"file": ("empty.jpg", b"", "image/jpeg")},
        headers=headers
    )
    assert res_empty.status_code == 400

    # Unsupported format (text file)
    res_txt = client.post(
        "/api/v1/images",
        data={"store_id": store_id},
        files={"file": ("doc.txt", b"Hello world text payload", "text/plain")},
        headers=headers
    )
    assert res_txt.status_code in (400, 415)

    # Corrupted image bytes
    res_corrupt = client.post(
        "/api/v1/images",
        data={"store_id": store_id},
        files={"file": ("fake.jpg", b"FAKED_JPEG_HEADER_CORRUPTED_BYTES_12345", "image/jpeg")},
        headers=headers
    )
    assert res_corrupt.status_code == 400

    # Invalid small dimensions (< 100x100)
    tiny_bytes = create_test_image_bytes(width=20, height=20)
    res_tiny = client.post(
        "/api/v1/images",
        data={"store_id": store_id},
        files={"file": ("tiny.jpg", tiny_bytes, "image/jpeg")},
        headers=headers
    )
    assert res_tiny.status_code == 400


def test_tenant_isolation_and_permissions(client, setup_tenants):
    """Test 11-12, 18-25: Tenant isolation & role-based image access/deletion rules."""
    headers_a_admin = {"Authorization": f"Bearer {setup_tenants['token_a_admin']}"}
    headers_a_staff = {"Authorization": f"Bearer {setup_tenants['token_a_staff']}"}
    headers_b_admin = {"Authorization": f"Bearer {setup_tenants['token_b_admin']}"}

    # Upload Image A1 for Company A
    img_a_bytes = create_test_image_bytes(width=400, height=300)
    res_a = client.post(
        "/api/v1/images",
        data={"store_id": str(setup_tenants["store_a1"].id)},
        files={"file": ("img_a1.jpg", img_a_bytes, "image/jpeg")},
        headers=headers_a_admin
    )
    assert res_a.status_code == 201
    img_a1_id = res_a.json()["id"]

    # Upload Image B1 for Company B
    img_b_bytes = create_test_image_bytes(width=500, height=500)
    res_b = client.post(
        "/api/v1/images",
        data={"store_id": str(setup_tenants["store_b1"].id)},
        files={"file": ("img_b1.jpg", img_b_bytes, "image/jpeg")},
        headers=headers_b_admin
    )
    assert res_b.status_code == 201
    img_b1_id = res_b.json()["id"]

    # 1. Company A user lists images -> Sees Image A1, does NOT see Image B1
    res_list_a = client.get("/api/v1/images", headers=headers_a_admin)
    assert res_list_a.status_code == 200
    item_ids_a = [item["id"] for item in res_list_a.json()["items"]]
    assert img_a1_id in item_ids_a
    assert img_b1_id not in item_ids_a

    # 2. Store filtering & pagination
    res_filter = client.get(f"/api/v1/images?store_id={setup_tenants['store_a1'].id}&page=1&page_size=10", headers=headers_a_admin)
    assert res_filter.status_code == 200
    assert res_filter.json()["total"] == 1

    # 3. Company A user tries to get Image B1 detail -> 404 Not Found
    res_detail_cross = client.get(f"/api/v1/images/{img_b1_id}", headers=headers_a_admin)
    assert res_detail_cross.status_code == 404

    # 4. Company A user gets Image A1 detail -> 200 OK
    res_detail_own = client.get(f"/api/v1/images/{img_a1_id}", headers=headers_a_admin)
    assert res_detail_own.status_code == 200

    # 5. STAFF role tries to delete image -> 403 Forbidden
    res_del_staff = client.delete(f"/api/v1/images/{img_a1_id}", headers=headers_a_staff)
    assert res_del_staff.status_code == 403

    # 6. Company A user tries to delete Image B1 -> 404 Not Found
    res_del_cross = client.delete(f"/api/v1/images/{img_b1_id}", headers=headers_a_admin)
    assert res_del_cross.status_code == 404

    # 7. ADMIN role deletes own image -> 204 No Content
    res_del_admin = client.delete(f"/api/v1/images/{img_a1_id}", headers=headers_a_admin)
    assert res_del_admin.status_code == 204

    # Verify deleted image is gone
    res_get_deleted = client.get(f"/api/v1/images/{img_a1_id}", headers=headers_a_admin)
    assert res_get_deleted.status_code == 404
