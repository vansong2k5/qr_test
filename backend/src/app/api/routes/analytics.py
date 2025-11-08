from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.product import Product
from app.models.qrcode import QrCode
from app.models.reuse_history import ReuseHistory
from app.models.scan_event import ScanEvent
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    QrAnalyticsResponse,
    QrTimelineEntry,
    SummaryStats,
)

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def analytics_summary(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    total_scans = db.query(func.count(ScanEvent.id)).scalar() or 0
    scans_today = (
        db.query(func.count(ScanEvent.id))
        .filter(func.date(ScanEvent.ts) == func.current_date())
        .scalar()
        or 0
    )
    active_qr = db.query(func.count(QrCode.id)).filter(QrCode.active.is_(True)).scalar() or 0
    reuse_cycles = db.query(func.coalesce(func.sum(QrCode.reuse_cycle), 0)).scalar() or 0
    scans_by_day = (
        db.query(func.date_trunc("day", ScanEvent.ts).label("day"), func.count(ScanEvent.id))
        .group_by("day")
        .order_by("day")
        .limit(30)
        .all()
    )
    return AnalyticsSummaryResponse(
        summary=SummaryStats(
            total_scans=total_scans,
            scans_today=scans_today,
            active_qr=active_qr,
            reuse_cycles=reuse_cycles,
        ),
        scans_by_day=[{"day": row.day.date(), "count": row[1]} for row in scans_by_day],
    )


@router.get("/qr/{code_id}", response_model=QrAnalyticsResponse)
async def qr_analytics(code_id: uuid.UUID, db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    qrcode = db.query(QrCode).filter(QrCode.id == code_id).first()
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    product_name = None
    if qrcode.product_id:
        product = db.query(Product).filter(Product.id == qrcode.product_id).first()
        product_name = product.name if product else None
    scan_events = (
        db.query(ScanEvent)
        .filter(ScanEvent.code_id == code_id)
        .order_by(ScanEvent.ts.asc())
        .all()
    )
    reuse_events = (
        db.query(ReuseHistory)
        .filter(ReuseHistory.code_id == code_id)
        .order_by(ReuseHistory.ts.asc())
        .all()
    )
    timeline: list[QrTimelineEntry] = []
    for ev in scan_events:
        timeline.append(
            QrTimelineEntry(
                ts=ev.ts,
                event="scan",
                reuse_cycle=ev.reuse_cycle_at_scan,
                meta={"ip": ev.ip, "device": ev.device},
            )
        )
    for ev in reuse_events:
        timeline.append(
            QrTimelineEntry(
                ts=ev.ts,
                event="reuse_start",
                reuse_cycle=ev.cycle,
                meta={"reason": ev.reason, "note": ev.note},
            )
        )
    timeline.sort(key=lambda entry: entry.ts)
    return QrAnalyticsResponse(
        code_id=str(code_id),
        product_name=product_name,
        total_scans=len(scan_events),
        timeline=timeline,
    )
