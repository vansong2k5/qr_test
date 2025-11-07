from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum("admin", "staff", name="user_role"), nullable=False, default="staff")
    created_at = Column(DateTime, default=datetime.utcnow)
