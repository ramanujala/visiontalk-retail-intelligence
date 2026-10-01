import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class RuleType:
    PRODUCT_REQUIRED = "PRODUCT_REQUIRED"
    PRODUCT_QUANTITY = "PRODUCT_QUANTITY"
    UNEXPECTED_PRODUCT = "UNEXPECTED_PRODUCT"
    PRODUCT_ZONE = "PRODUCT_ZONE"
    OCR_REQUIRED = "OCR_REQUIRED"
    CUSTOM_THRESHOLD = "CUSTOM_THRESHOLD"


class RuleSeverity:
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_EVALUATED = "NOT_EVALUATED"


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True)
    created_by = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    rule_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default=RuleSeverity.MEDIUM, index=True)
    configuration = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True, index=True)

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
    company = relationship("Company")
    store = relationship("Store")
    creator = relationship("User")
    findings = relationship("ComplianceFinding", back_populates="rule", cascade="all, delete-orphan")


class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(GUID(), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_run_id = Column(GUID(), ForeignKey("analysis_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(GUID(), ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False, index=True)

    status = Column(String(20), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=False, default=dict)
    evidence_references = Column(JSON, nullable=False, default=list)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    company = relationship("Company")
    store = relationship("Store")
    image = relationship("Image")
    analysis_run = relationship("AnalysisRun", back_populates="compliance_findings")
    rule = relationship("ComplianceRule", back_populates="findings")
