from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from ..models.scanevent import ScanEvent
from ..schemas.event import ScanEventOut


def log_event(
    db: Session,
    *,
    qrcode_id: int,
    ip: str | None,
    user_agent: str | None,
    referer: str | None,
    geo: dict[str, str | float | None] | None,
    extra: dict | None = None,
) -> ScanEvent:
    geo = geo or {}
    event = ScanEvent(
        qrcode_id=qrcode_id,
        scanned_at=datetime.utcnow(),
        ip=ip,
        user_agent=user_agent,
        referer=referer,
        geo_country=geo.get("country"),
        geo_city=geo.get("city"),
        lat=geo.get("lat"),
        lon=geo.get("lon"),
        extra=extra or {},
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
