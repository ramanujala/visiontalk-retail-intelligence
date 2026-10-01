import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text, JSON
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
    OCR = "OCR"
    EXPECTED_VS_ACTUAL = "EXPECTED_VS_ACTUAL"
    COMPLIANCE = "COMPLIANCE"


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
    ocr_results = relationship("OCRResult", back_populates="analysis_run", cascade="all, delete-orphan")
    expected_actual_items = relationship("ExpectedActualItem", back_populates="analysis_run", cascade="all, delete-orphan")
    expected_actual_issues = relationship("ExpectedActualIssue", back_populates="analysis_run", cascade="all, delete-orphan")
    compliance_findings = relationship("ComplianceFinding", back_populates="analysis_run", cascade="all, delete-orphan")


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


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    analysis_run_id = Column(GUID(), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)

    text = Column(Text, nullable=False)
    normalized_text = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    line_order = Column(Integer, nullable=False, default=0)

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
    analysis_run = relationship("AnalysisRun", back_populates="ocr_results")
    company = relationship("Company")


class ExpectedActualItemStatus:
    OBSERVED = "OBSERVED"
    MISSING = "MISSING"
    LOW_STOCK = "LOW_STOCK"
    EXCESS = "EXCESS"
    UNEXPECTED = "UNEXPECTED"
    UNMATCHED = "UNMATCHED"


class ExpectedActualIssueType:
    MISSING_PRODUCT = "MISSING_PRODUCT"
    LOW_STOCK = "LOW_STOCK"
    EXCESS_PRODUCT = "EXCESS_PRODUCT"
    UNEXPECTED_PRODUCT = "UNEXPECTED_PRODUCT"
    UNMATCHED_OBSERVATION = "UNMATCHED_OBSERVATION"


class ExpectedActualIssueSeverity:
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ExpectedActualItem(Base):
    __tablename__ = "expected_actual_items"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    analysis_run_id = Column(GUID(), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    expected_product_id = Column(GUID(), ForeignKey("expected_products.id", ondelete="SET NULL"), nullable=True, index=True)

    product_code = Column(String(100), nullable=False)
    product_name = Column(String(255), nullable=False)
    expected_quantity = Column(Integer, nullable=False, default=0)
    expected_min_quantity = Column(Integer, nullable=False, default=0)
    expected_max_quantity = Column(Integer, nullable=False, default=0)
    observed_quantity = Column(Integer, nullable=False, default=0)
    difference = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, index=True)

    evidence_references = Column(JSON, nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="expected_actual_items")
    company = relationship("Company")
    expected_product = relationship("ExpectedProduct")


class ExpectedActualIssue(Base):
    __tablename__ = "expected_actual_issues"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    analysis_run_id = Column(GUID(), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(GUID(), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    expected_product_id = Column(GUID(), ForeignKey("expected_products.id", ondelete="SET NULL"), nullable=True, index=True)

    issue_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=ExpectedActualIssueSeverity.MEDIUM, index=True)
    message = Column(Text, nullable=False)

    evidence_references = Column(JSON, nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    analysis_run = relationship("AnalysisRun", back_populates="expected_actual_issues")
    company = relationship("Company")
    store = relationship("Store")
    image = relationship("Image")
    expected_product = relationship("ExpectedProduct")

