from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=False)
    description = Column(String, nullable=True)
    lifecycle_status = Column(
        Enum(
            "manufactured",
            "in_warehouse",
            "in_store",
            "sold",
            "returned",
            "refurbished",
            "reused",
            "retired",
            name="lifecycle_status",
        ),
        nullable=False,
        default="manufactured",
    )
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", backref="products")
