from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class CustomerBase(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str | None = None
    meta: dict | None = Field(default_factory=dict)


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    meta: dict | None = None


class CustomerOut(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
