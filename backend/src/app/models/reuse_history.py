from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from sqlalchemy.dialects.postgresql import UUID
except Exception:  # pragma: no cover
    from sqlalchemy import String as UUID  # type: ignore

from app.db.base import Base


class ReuseHistory(Base):
    __tablename__ = "reuse_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("qrcodes.id"), index=True)
    cycle: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    qrcode = relationship("QrCode", back_populates="reuse_history")
