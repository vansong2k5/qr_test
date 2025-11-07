from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr


class CustomerBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    meta: dict[str, Any] | None = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerOut(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
