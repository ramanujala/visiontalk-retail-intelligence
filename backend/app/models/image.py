import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class ImageStatus:
    UPLOADING = "UPLOADING"
    VALIDATED = "VALIDATED"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"


class Image(Base):
    __tablename__ = "images"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    original_filename = Column(String(255), nullable=False)
    storage_key = Column(String(512), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    checksum = Column(String(64), nullable=False)

    status = Column(String(50), nullable=False, default=ImageStatus.READY, index=True)
    quality_score = Column(Integer, nullable=False, default=100)
    quality_flags = Column(JSON, nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="images")
    store = relationship("Store", back_populates="images")
    uploader = relationship("User", back_populates="images")
    analysis_runs = relationship("AnalysisRun", back_populates="image", cascade="all, delete-orphan")
