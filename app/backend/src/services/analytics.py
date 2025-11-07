from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..deps import get_current_user, get_db
from ..models.qrcode import QrCode
from ..models.scanevent import ScanEvent

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/overview")
async def overview(
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = None,
    db: Session = Depends(get_db),
):
    from_ = from_ or datetime.utcnow() - timedelta(days=7)
    to = to or datetime.utcnow()
    scan_count = db.query(func.count(ScanEvent.id)).filter(ScanEvent.scanned_at.between(from_, to)).scalar()
    unique_ip = db.query(func.count(func.distinct(ScanEvent.ip))).filter(ScanEvent.scanned_at.between(from_, to)).scalar()
    top_products = (
        db.query(QrCode.product_id, func.count(ScanEvent.id).label("scans"))
        .join(ScanEvent, ScanEvent.qrcode_id == QrCode.id)
        .group_by(QrCode.product_id)
        .order_by(func.count(ScanEvent.id).desc())
        .limit(5)
        .all()
    )
    return {
        "total_scans": scan_count,
        "unique_ip": unique_ip,
        "top_products": [dict(product_id=pid, scans=scans) for pid, scans in top_products],
    }


@router.get("/qrcode/{qr_id}")
async def qrcode_detail(qr_id: int, db: Session = Depends(get_db)):
    scans = (
        db.query(ScanEvent)
        .filter(ScanEvent.qrcode_id == qr_id)
        .order_by(ScanEvent.scanned_at.asc())
        .all()
    )
    return {
        "timeline": [
            {"at": scan.scanned_at.isoformat(), "geo_country": scan.geo_country, "allowed": scan.extra.get("allowed")}
            for scan in scans
        ],
        "total": len(scans),
    }
