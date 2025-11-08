from __future__ import annotations

import csv
import io
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.product import Product
from app.models.qrcode import QrCode
from app.models.scan_event import ScanEvent
from app.schemas.scan import ScanCreateResponse, ScanEventOut
from app.utils.rate_limit import rate_limiter

router = APIRouter()


def _detect_device(user_agent: str | None) -> str:
    if not user_agent:
        return "unknown"
    ua = user_agent.lower()
    if "iphone" in ua or "android" in ua:
        return "mobile"
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    return "desktop"


def _approx_geo_from_headers(headers) -> str | None:
    cf_country = headers.get("cf-ipcountry")
    if cf_country:
        return cf_country
    city = headers.get("x-appengine-city")
    region = headers.get("x-appengine-region")
    if city or region:
        return ",".join(filter(None, [city, region]))
    accept_language = headers.get("accept-language")
    if accept_language:
        return accept_language.split(",")[0]
    return None


@router.post("/scan", response_model=ScanCreateResponse)
async def register_scan(
    request: Request,
    code_id: uuid.UUID = Query(..., description="Mã QR"),
    db: Session = Depends(get_db_session),
):
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(f"{client_ip}:{code_id}")
    qrcode = db.query(QrCode).filter(QrCode.id == code_id, QrCode.active.is_(True)).first()
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR không tồn tại hoặc đã tắt")
    user_agent = request.headers.get("user-agent")
    event = ScanEvent(
        code_id=qrcode.id,
        ip=client_ip,
        user_agent=user_agent,
        referer=request.headers.get("referer"),
        approx_geo=_approx_geo_from_headers(request.headers),
        device=_detect_device(user_agent),
        reuse_cycle_at_scan=qrcode.reuse_cycle,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    product_name = None
    if qrcode.product_id:
        product = db.query(Product).filter(Product.id == qrcode.product_id).first()
        product_name = product.name if product else None
    return ScanCreateResponse(
        message="Đã ghi nhận lượt quét",
        product_name=product_name,
        reuse_cycle=qrcode.reuse_cycle,
    )


@router.get("/scan/{code_id}", response_class=HTMLResponse)
async def scan_page(code_id: uuid.UUID, db: Session = Depends(get_db_session)):
    qrcode = db.query(QrCode).filter(QrCode.id == code_id).first()
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR không tồn tại")
    product_name = None
    if qrcode.product_id:
        product = db.query(Product).filter(Product.id == qrcode.product_id).first()
        product_name = product.name if product else None
    html = f"""
    <html>
    <head><title>QR Info</title></head>
    <body>
        <h1>Thông tin sản phẩm</h1>
        <p>Mã: {code_id}</p>
        <p>Sản phẩm: {product_name or 'Chưa gắn'}</p>
        <p>Chu kỳ tái sử dụng: {qrcode.reuse_cycle}</p>
        <button onclick=\"fetch('/api/scan?code_id={code_id}',{{method:'POST'}}).then(()=>alert('Đã xác nhận!'))\">Xác nhận đã xem</button>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/scans", response_model=list[ScanEventOut])
async def list_scans(
    code_id: uuid.UUID | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    qs = db.query(ScanEvent)
    if code_id:
        qs = qs.filter(ScanEvent.code_id == code_id)
    if start:
        qs = qs.filter(ScanEvent.ts >= start)
    if end:
        qs = qs.filter(ScanEvent.ts <= end)
    return qs.order_by(ScanEvent.ts.desc()).limit(500).all()


@router.get("/export/scans.csv")
async def export_scans(
    code_id: uuid.UUID | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    qs = db.query(ScanEvent)
    if code_id:
        qs = qs.filter(ScanEvent.code_id == code_id)
    if start:
        qs = qs.filter(ScanEvent.ts >= start)
    if end:
        qs = qs.filter(ScanEvent.ts <= end)
    events = qs.order_by(ScanEvent.ts.desc()).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "code_id", "ts", "ip", "device", "approx_geo"])
    for ev in events:
        writer.writerow([ev.id, ev.code_id, ev.ts.isoformat(), ev.ip, ev.device, ev.approx_geo])
    buffer.seek(0)
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv")
