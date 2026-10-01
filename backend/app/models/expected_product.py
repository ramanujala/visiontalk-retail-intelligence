import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class ExpectedProduct(Base):
    __tablename__ = "expected_products"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    company_id = Column(GUID(), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(GUID(), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)

    product_name = Column(String(255), nullable=False)
    product_code = Column(String(100), nullable=False, index=True)
    expected_quantity = Column(Integer, nullable=False, default=1)
    expected_min_quantity = Column(Integer, nullable=False, default=1)
    expected_max_quantity = Column(Integer, nullable=False, default=10)
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

    __table_args__ = (
        UniqueConstraint("company_id", "store_id", "product_code", name="uix_company_store_product_code"),
    )
