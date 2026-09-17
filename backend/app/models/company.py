import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class Company(Base):
    __tablename__ = "companies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    stores = relationship("Store", back_populates="company", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="company", cascade="all, delete-orphan")
    analysis_runs = relationship("AnalysisRun", back_populates="company", cascade="all, delete-orphan")
