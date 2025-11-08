from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class QrCode(Base):
    __tablename__ = "qrcodes"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)
    payload = Column(JSON, default=dict)
    reusable_mode = Column(Enum("unlimited", "limited", "phase", name="reusable_mode"), nullable=False)
    reuse_limit = Column(Integer, nullable=True)
    reuse_count = Column(Integer, default=0)
    lifecycle_policy = Column(JSON, nullable=True)
    image_mask_path = Column(String, nullable=True)
    image_render_path = Column(String, nullable=True)
    image_svg_path = Column(String, nullable=True)
    status = Column(Enum("active", "inactive", "revoked", name="qr_status"), default="active")
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    lifecycle_state = Column(
        Enum("issued", "active", "suspended", "retired", "recycled", name="qr_lifecycle_state"),
        default="issued",
        nullable=False,
    )
    activated_at = Column(DateTime, nullable=True)
    retired_at = Column(DateTime, nullable=True)

    product = relationship("Product", backref="qrcodes")
    creator = relationship("User")
    lifecycle_events = relationship(
        "QrLifecycleEvent",
        back_populates="qrcode",
        cascade="all, delete-orphan",
        order_by="QrLifecycleEvent.occurred_at.desc()",
    )
