from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.company import Company
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterCompanyRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register_company(payload: RegisterCompanyRequest, db: Session = Depends(get_db)):
    """Atomically registers a new company tenant and its primary administrator account."""
    # Check duplicate company slug
    existing_company = db.query(Company).filter(Company.slug == payload.company_slug).first()
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug is already registered."
        )

    # Check duplicate user email (globally unique)
    existing_user = db.query(User).filter(User.email == payload.admin_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email is already registered."
        )

    # Atomic transaction
    try:
        new_company = Company(
            name=payload.company_name,
            slug=payload.company_slug
        )
        db.add(new_company)
        db.flush()  # Generate company.id

        hashed_pwd = hash_password(payload.admin_password)
        admin_user = User(
            company_id=new_company.id,
            email=payload.admin_email,
            password_hash=hashed_pwd,
            full_name=payload.admin_full_name,
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register company and admin user."
        ) from e

    token = create_access_token(
        data={
            "sub": str(admin_user.id),
            "company_id": str(admin_user.company_id),
            "role": admin_user.role
        }
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user credentials and returns JWT access token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive."
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "company_id": str(user.company_id),
            "role": user.role
        }
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile and company details of current authenticated user."""
    return current_user
