from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    sku: str
    name: str
    description: str | None = None
    owner_customer_id: int | None = None
    meta: dict | None = Field(default_factory=dict)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: str | None = None
    name: str | None = None
    description: str | None = None
    owner_customer_id: int | None = None
    meta: dict | None = None


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
