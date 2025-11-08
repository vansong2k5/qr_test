from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class ScanEventOut(BaseModel):
    id: int
    code_id: uuid.UUID
    ts: datetime
    ip: str | None
    user_agent: str | None
    referer: str | None
    approx_geo: str | None
    device: str | None
    reuse_cycle_at_scan: int

    class Config:
        orm_mode = True


class ScanCreateResponse(BaseModel):
    message: str
    product_name: str | None
    reuse_cycle: int
