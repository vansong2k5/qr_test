from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ProductBase(BaseModel):
    customer_id: int
    name: str
    sku: str
    description: Optional[str] = None
    lifecycle_status: str = "manufactured"
    meta: dict[str, Any] | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductOut(ProductBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
