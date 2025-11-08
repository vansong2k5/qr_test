from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class QrOptions(BaseModel):
    size: int = 400
    ecc: str = Field(default="H", regex="^[LMQH]$")
    fg_color: str = "#000000"
    bg_color: str = "#FFFFFF"
    margin: int = 4
    threshold: int | None = None
    logo_enabled: bool = False


class QrGenerateRequest(BaseModel):
    product_id: int | None = None
    customer_id: int | None = None
    data: dict | str
    reuse_allowed: bool = False
    options: QrOptions = Field(default_factory=QrOptions)


class QrOut(BaseModel):
    code_id: uuid.UUID
    product_id: int | None
    customer_id: int | None
    reuse_allowed: bool
    reuse_cycle: int
    active: bool
    version: int
    ecc: str
    image_url_png: str
    image_url_svg: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class QrUpdateRequest(BaseModel):
    active: bool | None = None
    product_id: int | None = None
    customer_id: int | None = None
    reuse_allowed: bool | None = None


class ReuseStartRequest(BaseModel):
    reason: str
    note: str | None = None


class ReuseHistoryOut(BaseModel):
    cycle: int
    reason: str | None
    note: str | None
    ts: datetime

    class Config:
        orm_mode = True
