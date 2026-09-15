from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import hash_password


def test_store_crud_flow(client: TestClient):
    # Register Company A Admin
    reg_payload = {
        "company_name": "Store Corp A",
        "company_slug": "store-corp-a",
        "admin_email": "admin@storecorpa.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin A"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    token_a = reg_res.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 1. Create Store A1
    create_res = client.post(
        "/api/v1/stores",
        json={"name": "Downtown Market", "code": "STR-001", "location": "123 Main St"},
        headers=headers_a
    )
    assert create_res.status_code == 201
    store_a1 = create_res.json()
    assert store_a1["name"] == "Downtown Market"
    assert store_a1["code"] == "STR-001"
    store_a1_id = store_a1["id"]

    # 2. List Stores for Company A
    list_res = client.get("/api/v1/stores", headers=headers_a)
    assert list_res.status_code == 200
    stores_list = list_res.json()
    assert len(stores_list) == 1
    assert stores_list[0]["id"] == store_a1_id

    # 3. Get Store A1
    get_res = client.get(f"/api/v1/stores/{store_a1_id}", headers=headers_a)
    assert get_res.status_code == 200
    assert get_res.json()["code"] == "STR-001"

    # 4. Update Store A1
    patch_res = client.patch(
        f"/api/v1/stores/{store_a1_id}",
        json={"name": "Downtown Supermarket"},
        headers=headers_a
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["name"] == "Downtown Supermarket"

    # 5. Delete Store A1
    del_res = client.delete(f"/api/v1/stores/{store_a1_id}", headers=headers_a)
    assert del_res.status_code == 204

    # Verify deleted
    get_after_del = client.get(f"/api/v1/stores/{store_a1_id}", headers=headers_a)
    assert get_after_del.status_code == 404


def test_duplicate_store_code_handling(client: TestClient):
    # Register Company A
    token_a = client.post("/api/v1/auth/register", json={
        "company_name": "Company Dup A",
        "company_slug": "dup-a",
        "admin_email": "admin@dupa.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin Dup A"
    }).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Register Company B
    token_b = client.post("/api/v1/auth/register", json={
        "company_name": "Company Dup B",
        "company_slug": "dup-b",
        "admin_email": "admin@dupb.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin Dup B"
    }).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Create Store 'CODE-X' in Company A
    res_a1 = client.post("/api/v1/stores", json={"name": "Store A", "code": "CODE-X"}, headers=headers_a)
    assert res_a1.status_code == 201

    # Duplicate Store 'CODE-X' in SAME Company A -> Rejected 400
    res_a2 = client.post("/api/v1/stores", json={"name": "Store A2", "code": "CODE-X"}, headers=headers_a)
    assert res_a2.status_code == 400
    assert "already exists in your company" in res_a2.json()["error"]["message"]

    # Same Store 'CODE-X' in DIFFERENT Company B -> Allowed 201
    res_b1 = client.post("/api/v1/stores", json={"name": "Store B", "code": "CODE-X"}, headers=headers_b)
    assert res_b1.status_code == 201


def test_strict_cross_tenant_isolation(client: TestClient):
    """CRITICAL SECURITY TEST: Company A JWT attempting to access Company B store MUST receive 404 Not Found."""
    # Setup Company A
    token_a = client.post("/api/v1/auth/register", json={
        "company_name": "Iso Corp A",
        "company_slug": "iso-corp-a",
        "admin_email": "admin@isocorpa.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin A"
    }).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Setup Company B and create Store B1
    token_b = client.post("/api/v1/auth/register", json={
        "company_name": "Iso Corp B",
        "company_slug": "iso-corp-b",
        "admin_email": "admin@isocorpb.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin B"
    }).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    store_b1_res = client.post(
        "/api/v1/stores",
        json={"name": "Company B Store", "code": "STORE-B1"},
        headers=headers_b
    )
    assert store_b1_res.status_code == 201
    store_b1_id = store_b1_res.json()["id"]

    # Company A attempts to GET Company B's store -> 404 NOT FOUND
    cross_get_res = client.get(f"/api/v1/stores/{store_b1_id}", headers=headers_a)
    assert cross_get_res.status_code == 404
    assert cross_get_res.json()["error"]["message"] == "Store not found."

    # Company A attempts to PATCH Company B's store -> 404 NOT FOUND
    cross_patch_res = client.patch(
        f"/api/v1/stores/{store_b1_id}",
        json={"name": "Hacked Store Name"},
        headers=headers_a
    )
    assert cross_patch_res.status_code == 404

    # Company A attempts to DELETE Company B's store -> 404 NOT FOUND
    cross_del_res = client.delete(f"/api/v1/stores/{store_b1_id}", headers=headers_a)
    assert cross_del_res.status_code == 404

    # Company A lists stores -> Returns ONLY Company A stores (0 stores)
    list_a_res = client.get("/api/v1/stores", headers=headers_a)
    assert list_a_res.status_code == 200
    assert len(list_a_res.json()) == 0


def test_role_authorization_restrictions(client: TestClient, db_session: Session):
    """Verifies STAFF role is restricted from admin-only operations (403 Forbidden)."""
    reg_res = client.post("/api/v1/auth/register", json={
        "company_name": "Role Corp",
        "company_slug": "role-corp",
        "admin_email": "admin@rolecorp.com",
        "admin_password": "Password123!",
        "admin_full_name": "Admin Role"
    })
    token_admin = reg_res.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    # Create Store as Admin
    store_res = client.post(
        "/api/v1/stores",
        json={"name": "Role Store", "code": "ROLE-01"},
        headers=headers_admin
    )
    store_id = store_res.json()["id"]

    # Create a STAFF user in the same company
    admin_user = db_session.query(User).filter(User.email == "admin@rolecorp.com").first()
    staff_user = User(
        company_id=admin_user.company_id,
        email="staff@rolecorp.com",
        password_hash=hash_password("Password123!"),
        full_name="Staff Worker",
        role=UserRole.STAFF,
        is_active=True
    )
    db_session.add(staff_user)
    db_session.commit()

    # Login as Staff
    staff_token = client.post("/api/v1/auth/login", json={
        "email": "staff@rolecorp.com",
        "password": "Password123!"
    }).json()["access_token"]
    headers_staff = {"Authorization": f"Bearer {staff_token}"}

    # Staff can read stores
    staff_get = client.get(f"/api/v1/stores/{store_id}", headers=headers_staff)
    assert staff_get.status_code == 200

    # Staff attempts to create store -> 403 Forbidden
    staff_create = client.post(
        "/api/v1/stores",
        json={"name": "Unauthorized Store", "code": "UNAUTH"},
        headers=headers_staff
    )
    assert staff_create.status_code == 403

    # Staff attempts to delete store -> 403 Forbidden
    staff_del = client.delete(f"/api/v1/stores/{store_id}", headers=headers_staff)
    assert staff_del.status_code == 403
