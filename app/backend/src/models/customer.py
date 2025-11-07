from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String

from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    meta = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
