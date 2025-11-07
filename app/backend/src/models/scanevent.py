from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class ScanEvent(Base):
    __tablename__ = "scanevents"

    id = Column(Integer, primary_key=True)
    qrcode_id = Column(Integer, ForeignKey("qrcodes.id"), index=True, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow, index=True)
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    referer = Column(String, nullable=True)
    geo_country = Column(String, nullable=True)
    geo_city = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    extra = Column(JSON, default=dict)

    qrcode = relationship("QrCode", backref="scans")
