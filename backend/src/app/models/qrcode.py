from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from sqlalchemy.dialects.postgresql import JSONB, UUID
except Exception:  # pragma: no cover
    from sqlalchemy import JSON as JSONB  # type: ignore
    from sqlalchemy import String as UUID  # type: ignore

from app.db.base import Base


class QrCode(Base):
    __tablename__ = "qrcodes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"), nullable=True, index=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"), nullable=True, index=True)
    data_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    data_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    reuse_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    reuse_cycle: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    ecc: Mapped[str] = mapped_column(String(2), default="H")
    image_path_png: Mapped[str] = mapped_column(String(255), nullable=False)
    image_path_svg: Mapped[str] = mapped_column(String(255), nullable=False)
    mask_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    logo_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    product = relationship("Product", back_populates="qrcodes")
    customer = relationship("Customer", back_populates="qrcodes")
    scan_events = relationship("ScanEvent", back_populates="qrcode", cascade="all, delete-orphan")
    reuse_history = relationship(
        "ReuseHistory", back_populates="qrcode", cascade="all, delete-orphan", order_by="ReuseHistory.ts"
    )
