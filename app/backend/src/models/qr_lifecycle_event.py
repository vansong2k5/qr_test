from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship

from .database import Base


class QrLifecycleEvent(Base):
    __tablename__ = "qr_lifecycle_events"

    id = Column(Integer, primary_key=True)
    qrcode_id = Column(Integer, ForeignKey("qrcodes.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(
        Enum(
            "created",
            "updated",
            "status_changed",
            "scan_recorded",
            "reuse_incremented",
            "revoked",
            "activated",
            "retired",
            "esg_tagged",
            name="qr_event_type",
        ),
        nullable=False,
    )
    occurred_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata = Column(JSON, nullable=True)

    qrcode = relationship("QrCode", back_populates="lifecycle_events")
    actor = relationship("User")
