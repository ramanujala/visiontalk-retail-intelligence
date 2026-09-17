import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class AnalysisRunStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AnalysisType:
    OBJECT_DETECTION = "OBJECT_DETECTION"


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(GUID(), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    initiated_by = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    analysis_type = Column(String(50), nullable=False, default=AnalysisType.OBJECT_DETECTION, index=True)
    status = Column(String(50), nullable=False, default=AnalysisRunStatus.PENDING, index=True)
    model_name = Column(String(100), nullable=False, default="YOLOv8")
    model_version = Column(String(100), nullable=False, default="yolov8n")

    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

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
    company = relationship("Company", back_populates="analysis_runs")
    image = relationship("Image", back_populates="analysis_runs")
    initiator = relationship("User", back_populates="analysis_runs")
    detections = relationship("Detection", back_populates="analysis_run", cascade="all, delete-orphan")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    analysis_run_id = Column(GUID(), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    class_id = Column(Integer, nullable=False)
    class_name = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False)

    x_min = Column(Float, nullable=False)
    y_min = Column(Float, nullable=False)
    x_max = Column(Float, nullable=False)
    y_max = Column(Float, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="detections")
    company = relationship("Company")
