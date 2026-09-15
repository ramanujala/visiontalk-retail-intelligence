from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.store import Store
from app.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.post("", response_model=StoreResponse, status_code=status.HTTP_201_CREATED)
def create_store(
    payload: StoreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Creates a new store within current authenticated user's company."""
    # Check duplicate store code inside the SAME company tenant
    existing_store = db.query(Store).filter(
        Store.company_id == current_user.company_id,
        Store.code == payload.code
    ).first()
    
    if existing_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Store code '{payload.code}' already exists in your company."
        )

    new_store = Store(
        company_id=current_user.company_id,
        name=payload.name,
        code=payload.code,
        location=payload.location
    )
    db.add(new_store)
    db.commit()
    db.refresh(new_store)
    return new_store


@router.get("", response_model=List[StoreResponse])
def list_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists all stores belonging strictly to current authenticated user's company tenant."""
    stores = db.query(Store).filter(Store.company_id == current_user.company_id).all()
    return stores


@router.get("/{store_id}", response_model=StoreResponse)
def get_store(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves a store by ID enforcing strict company tenant isolation."""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.company_id == current_user.company_id
    ).first()

    if not store:
        # Crucial security rule: Return 404 to avoid leaking cross-tenant resource existence
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    return store


@router.patch("/{store_id}", response_model=StoreResponse)
def update_store(
    store_id: UUID,
    payload: StoreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Updates store details enforcing company tenant isolation."""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.company_id == current_user.company_id
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    if payload.code is not None and payload.code != store.code:
        duplicate = db.query(Store).filter(
            Store.company_id == current_user.company_id,
            Store.code == payload.code,
            Store.id != store_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Store code '{payload.code}' already exists in your company."
            )
        store.code = payload.code

    if payload.name is not None:
        store.name = payload.name
    if payload.location is not None:
        store.location = payload.location
    if payload.is_active is not None:
        store.is_active = payload.is_active

    db.commit()
    db.refresh(store)
    return store


@router.delete("/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_store(
    store_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN]))
):
    """Deletes a store within current user's company tenant (Admin only)."""
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.company_id == current_user.company_id
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    db.delete(store)
    db.commit()
    return None
