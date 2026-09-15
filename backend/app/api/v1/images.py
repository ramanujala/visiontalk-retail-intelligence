import io
import uuid
import math
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.store import Store
from app.models.image import Image, ImageStatus
from app.schemas.image import ImageResponse, ImageListResponse
from app.api.deps import get_current_user, require_role
from app.services.storage.local import LocalStorageProvider
from app.services.image_processor import (
    validate_file_header_and_size,
    decode_and_validate_image,
    calculate_sha256,
    assess_image_quality,
    ImageValidationError
)

router = APIRouter(prefix="/images", tags=["Images"])

# Instantiated Storage Provider
storage_provider = LocalStorageProvider(base_dir=settings.STORAGE_DIR)


@router.post("", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    store_id: UUID = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Uploads, validates, assesses quality, stores file securely, and records metadata for an image."""
    # 1. Validate Store Tenant Ownership
    store = db.query(Store).filter(
        Store.id == store_id,
        Store.company_id == current_user.company_id
    ).first()

    if not store:
        # Crucial Tenant Isolation Rule: Return 404 if store is nonexistent or belongs to another company
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found."
        )

    # Read uploaded file content into bytes
    try:
        file_bytes = await file.read()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file payload."
        )

    # 2. File Header & Size Validation
    try:
        validate_file_header_and_size(
            file_bytes=file_bytes,
            filename=file.filename or "upload.jpg",
            content_type=file.content_type or ""
        )
    except ImageValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # 3. Image Decoding & Resolution Validation
    try:
        pil_img, detected_mime, width, height = decode_and_validate_image(file_bytes)
    except ImageValidationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)

    # 4. Checksum & Quality Assessment
    checksum = calculate_sha256(file_bytes)
    quality_score, quality_flags = assess_image_quality(file_bytes)

    # 5. Secure Physical Storage Key Generation
    image_uuid = uuid.uuid4()
    ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    file_ext = ext_map.get(detected_mime, ".jpg")
    storage_filename = f"{image_uuid}{file_ext}"

    # Folder structure: {company_id}/{store_id}
    tenant_folder = f"{current_user.company_id}/{store_id}"

    # Save to storage provider
    try:
        storage_key = storage_provider.save_file(
            file_data=io.BytesIO(file_bytes),
            filename=storage_filename,
            destination_folder=tenant_folder
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist image to secure storage backend."
        )

    # 6. Create Database Record
    image_record = Image(
        id=image_uuid,
        company_id=current_user.company_id,
        store_id=store_id,
        uploaded_by=current_user.id,
        original_filename=file.filename or storage_filename,
        storage_key=storage_key,
        mime_type=detected_mime,
        file_size=len(file_bytes),
        width=width,
        height=height,
        checksum=checksum,
        status=ImageStatus.READY,
        quality_score=quality_score,
        quality_flags=quality_flags
    )

    try:
        db.add(image_record)
        db.commit()
        db.refresh(image_record)
    except Exception as db_err:
        # Atomic Cleanup: Remove saved physical file if DB transaction fails
        storage_provider.delete_file(storage_key)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist image metadata to database."
        )

    return image_record


@router.get("", response_model=ImageListResponse)
def list_images(
    store_id: Optional[UUID] = Query(None, description="Filter by store ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists images with tenant isolation, optional filtering, and pagination."""
    query = db.query(Image).filter(Image.company_id == current_user.company_id)

    if store_id:
        # Verify store belongs to current user's company tenant
        store = db.query(Store).filter(
            Store.id == store_id,
            Store.company_id == current_user.company_id
        ).first()
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Store not found."
            )
        query = query.filter(Image.store_id == store_id)

    if status_filter:
        query = query.filter(Image.status == status_filter.upper())
    else:
        # By default exclude soft-deleted images from standard listing
        query = query.filter(Image.status != ImageStatus.DELETED)

    total = query.count()
    pages = math.ceil(total / page_size) if total > 0 else 0

    items = query.order_by(Image.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return ImageListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


@router.get("/{image_id}", response_model=ImageResponse)
def get_image_detail(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves safe image metadata enforcing strict company tenant isolation."""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.company_id == current_user.company_id,
        Image.status != ImageStatus.DELETED
    ).first()

    if not image:
        # Crucial security rule: Return 404 to avoid leaking cross-tenant resource existence
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found."
        )

    return image


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Deletes an image and its physical storage object (ADMIN and MANAGER only)."""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.company_id == current_user.company_id,
        Image.status != ImageStatus.DELETED
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found."
        )

    # 1. Delete physical storage object (handles missing files gracefully)
    try:
        storage_provider.delete_file(image.storage_key)
    except Exception:
        pass

    # 2. Mark database record as DELETED (or delete row)
    db.delete(image)
    db.commit()

    return None
