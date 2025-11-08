from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class QrBase(BaseModel):
    payload: dict[str, Any] | None = None
    reusable_mode: str
    reuse_limit: Optional[int] = None
    lifecycle_policy: dict[str, Any] | None = None
    status: str = "active"


class QrCreate(QrBase):
    product_id: int


class QrUpdate(BaseModel):
    payload: dict[str, Any] | None = None
    reusable_mode: Optional[str] = None
    reuse_limit: Optional[int] = None
    lifecycle_policy: dict[str, Any] | None = None
    status: Optional[str] = None
    lifecycle_state: Optional[str] = None


class QrLifecycleEventOut(BaseModel):
    id: int
    qrcode_id: int
    event_type: str
    occurred_at: datetime
    actor_id: Optional[int] = None
    metadata: dict[str, Any] | None = None

    class Config:
        orm_mode = True


class QrOut(QrBase):
    product_id: int
    id: int
    code: str
    reuse_count: int
    image_mask_path: Optional[str] = None
    image_render_path: Optional[str] = None
    image_svg_path: Optional[str] = None
    created_by: int
    created_at: datetime
    lifecycle_state: str
    activated_at: Optional[datetime] = None
    retired_at: Optional[datetime] = None
    lifecycle_events: list[QrLifecycleEventOut] = []

    class Config:
        orm_mode = True
