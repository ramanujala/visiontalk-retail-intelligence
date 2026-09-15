from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.company import Company
from app.models.user import User, UserRole
from app.core.security import verify_password


def test_company_registration_success(client: TestClient, db_session: Session):
    payload = {
        "company_name": "Vision Retail Inc",
        "company_slug": "vision-retail",
        "admin_email": "admin@visionretail.com",
        "admin_password": "SecurePassword123!",
        "admin_full_name": "Alice Admin"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify DB records created atomically
    company = db_session.query(Company).filter(Company.slug == "vision-retail").first()
    assert company is not None
    assert company.name == "Vision Retail Inc"

    user = db_session.query(User).filter(User.email == "admin@visionretail.com").first()
    assert user is not None
    assert user.company_id == company.id
    assert user.role == UserRole.ADMIN
    assert user.is_active is True
    # Password hashing check
    assert user.password_hash != "SecurePassword123!"
    assert verify_password("SecurePassword123!", user.password_hash) is True


def test_duplicate_company_slug_rejected(client: TestClient):
    payload = {
        "company_name": "Vision Retail Inc",
        "company_slug": "duplicate-slug",
        "admin_email": "admin1@test.com",
        "admin_password": "SecurePassword123!",
        "admin_full_name": "Admin One"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    payload["admin_email"] = "admin2@test.com"
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "Company slug is already registered" in res2.json()["error"]["message"]


def test_duplicate_email_rejected(client: TestClient):
    payload = {
        "company_name": "Company One",
        "company_slug": "company-one",
        "admin_email": "shared@admin.com",
        "admin_password": "SecurePassword123!",
        "admin_full_name": "Admin One"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    payload["company_name"] = "Company Two"
    payload["company_slug"] = "company-two"
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "User email is already registered" in res2.json()["error"]["message"]


def test_login_success_and_failure(client: TestClient):
    # Register user first
    reg_payload = {
        "company_name": "Auth Retail",
        "company_slug": "auth-retail",
        "admin_email": "user@authretail.com",
        "admin_password": "Password123!",
        "admin_full_name": "Bob Auth"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    # Valid Login
    login_res = client.post("/api/v1/auth/login", json={
        "email": "user@authretail.com",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # Invalid Password Login
    bad_pwd_res = client.post("/api/v1/auth/login", json={
        "email": "user@authretail.com",
        "password": "WrongPassword!"
    })
    assert bad_pwd_res.status_code == 401
    assert "Invalid email or password" in bad_pwd_res.json()["error"]["message"]

    # Non-existent User Login
    no_user_res = client.post("/api/v1/auth/login", json={
        "email": "nonexistent@test.com",
        "password": "Password123!"
    })
    assert no_user_res.status_code == 401


def test_get_me_profile(client: TestClient):
    reg_payload = {
        "company_name": "Me Corp",
        "company_slug": "me-corp",
        "admin_email": "me@mecorp.com",
        "admin_password": "Password123!",
        "admin_full_name": "Me User"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    # Without Token -> 401
    no_token_res = client.get("/api/v1/auth/me")
    assert no_token_res.status_code == 401

    # With Valid Token -> 200
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    data = me_res.json()
    assert data["email"] == "me@mecorp.com"
    assert data["role"] == "ADMIN"
    assert data["company"]["slug"] == "me-corp"
    assert "password_hash" not in data  # Never leak password hash


def test_inactive_user_rejected(client: TestClient, db_session: Session):
    reg_payload = {
        "company_name": "Inactive Corp",
        "company_slug": "inactive-corp",
        "admin_email": "inactive@corp.com",
        "admin_password": "Password123!",
        "admin_full_name": "Inactive User"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    # Deactivate user in DB
    user = db_session.query(User).filter(User.email == "inactive@corp.com").first()
    user.is_active = False
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/v1/auth/me", headers=headers)
    assert res.status_code == 401
    assert "deactivated" in res.json()["error"]["message"]
