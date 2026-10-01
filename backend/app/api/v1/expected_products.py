from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.expected_product import ExpectedProduct
from app.schemas.expected_actual import (
    ExpectedProductCreate,
    ExpectedProductUpdate,
    ExpectedProductResponse
)
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/expected-products", tags=["Expected Products"])


@router.post("", response_model=ExpectedProductResponse, status_code=status.HTTP_201_CREATED)
def create_expected_product(
    payload: ExpectedProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Creates a new expected product configuration for a store (ADMIN/MANAGER)."""
    # Verify target store belongs to current user's company
    store = db.query(Store).filter(
        Store.id == payload.store_id,
        Store.company_id == current_user.company_id
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    # Check duplicate product_code in same store & company
    existing = db.query(ExpectedProduct).filter(
        ExpectedProduct.company_id == current_user.company_id,
        ExpectedProduct.store_id == payload.store_id,
        ExpectedProduct.product_code == payload.product_code
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expected product code '{payload.product_code}' already exists for this store."
        )

    product = ExpectedProduct(
        company_id=current_user.company_id,
        store_id=payload.store_id,
        product_name=payload.product_name,
        product_code=payload.product_code,
        expected_quantity=payload.expected_quantity,
        expected_min_quantity=payload.expected_min_quantity,
        expected_max_quantity=payload.expected_max_quantity,
        is_active=payload.is_active
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("", response_model=List[ExpectedProductResponse])
def list_expected_products(
    store_id: Optional[UUID] = Query(None, description="Filter by store ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists expected product configurations for current user's company tenant."""
    query = db.query(ExpectedProduct).filter(ExpectedProduct.company_id == current_user.company_id)

    if store_id:
        # Verify store ownership
        store = db.query(Store).filter(
            Store.id == store_id,
            Store.company_id == current_user.company_id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found."
            )
        query = query.filter(ExpectedProduct.store_id == store_id)

    if is_active is not None:
        query = query.filter(ExpectedProduct.is_active == is_active)

    return query.order_by(ExpectedProduct.created_at.desc()).all()


@router.get("/{product_id}", response_model=ExpectedProductResponse)
def get_expected_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves an expected product by ID enforcing company tenant isolation."""
    product = db.query(ExpectedProduct).filter(
        ExpectedProduct.id == product_id,
        ExpectedProduct.company_id == current_user.company_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expected product not found."
        )

    return product


@router.put("/{product_id}", response_model=ExpectedProductResponse)
def update_expected_product(
    product_id: UUID,
    payload: ExpectedProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Updates an expected product configuration (ADMIN/MANAGER)."""
    product = db.query(ExpectedProduct).filter(
        ExpectedProduct.id == product_id,
        ExpectedProduct.company_id == current_user.company_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expected product not found."
        )

    if payload.product_code and payload.product_code != product.product_code:
        duplicate = db.query(ExpectedProduct).filter(
            ExpectedProduct.company_id == current_user.company_id,
            ExpectedProduct.store_id == product.store_id,
            ExpectedProduct.product_code == payload.product_code,
            ExpectedProduct.id != product_id
        ).first()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Expected product code '{payload.product_code}' already exists for this store."
            )
        product.product_code = payload.product_code

    if payload.product_name is not None:
        product.product_name = payload.product_name
    if payload.expected_quantity is not None:
        product.expected_quantity = payload.expected_quantity
    if payload.expected_min_quantity is not None:
        product.expected_min_quantity = payload.expected_min_quantity
    if payload.expected_max_quantity is not None:
        product.expected_max_quantity = payload.expected_max_quantity
    if payload.is_active is not None:
        product.is_active = payload.is_active

    # Validate min <= max if both are set
    if product.expected_max_quantity < product.expected_min_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expected_max_quantity cannot be less than expected_min_quantity"
        )

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expected_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Deletes an expected product configuration (ADMIN/MANAGER)."""
    product = db.query(ExpectedProduct).filter(
        ExpectedProduct.id == product_id,
        ExpectedProduct.company_id == current_user.company_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expected product not found."
        )

    db.delete(product)
    db.commit()
    return None
