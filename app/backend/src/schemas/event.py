from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class ScanEventOut(BaseModel):
    id: int
    qrcode_id: int
    scanned_at: datetime
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    geo_country: Optional[str] = None
    geo_city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    extra: dict[str, Any] | None = None

    class Config:
        orm_mode = True
