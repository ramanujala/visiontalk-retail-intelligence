import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class Store(Base):
    __tablename__ = "stores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=False)
    location = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    company = relationship("Company", back_populates="stores")
    images = relationship("Image", back_populates="store", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uix_company_store_code"),
    )
