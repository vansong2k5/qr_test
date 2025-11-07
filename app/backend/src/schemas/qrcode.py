from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class QrBase(BaseModel):
    product_id: int
    payload: dict[str, Any] | None = None
    reusable_mode: str
    reuse_limit: Optional[int] = None
    lifecycle_policy: dict[str, Any] | None = None
    status: str = "active"


class QrCreate(QrBase):
    pass


class QrUpdate(QrBase):
    pass


class QrOut(QrBase):
    id: int
    code: str
    reuse_count: int
    image_mask_path: Optional[str] = None
    image_render_path: Optional[str] = None
    image_svg_path: Optional[str] = None
    created_by: int
    created_at: datetime

    class Config:
        orm_mode = True
