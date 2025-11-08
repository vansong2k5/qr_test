from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..crud.qrcode import qr as qr_crud
from ..crud.scanevent import log_event
from ..deps import get_current_user, get_db
from ..lifecycle.events import log_qr_lifecycle_event
from ..models.product import Product
from ..schemas.event import ScanEventOut

router = APIRouter()
public_router = APIRouter()


@router.get("/logs", response_model=list[ScanEventOut], dependencies=[Depends(get_current_user)])
async def list_events(db: Session = Depends(get_db)):
    from ..models.scanevent import ScanEvent

    return db.query(ScanEvent).order_by(ScanEvent.scanned_at.desc()).limit(100).all()


@public_router.get("/s/{code}", response_class=HTMLResponse)
async def scan_redirect(code: str, request: Request, db: Session = Depends(get_db)):
    qrcode = qr_crud.get_by_code(db, code=code)
    if not qrcode or qrcode.status == "revoked":
        return HTMLResponse("<h1>QR code invalid</h1>", status_code=404)

    product = db.query(Product).filter(Product.id == qrcode.product_id).first()
    if not product:
        return HTMLResponse("<h1>Product missing</h1>", status_code=404)

    allowed = True
    message = ""
    if qrcode.reusable_mode == "limited":
        if qrcode.reuse_limit is not None and qrcode.reuse_count >= qrcode.reuse_limit:
            allowed = False
            message = "Usage limit exceeded"
    elif qrcode.reusable_mode == "phase":
        policy = qrcode.lifecycle_policy or {}
        allowed_statuses = policy.get("allowed_statuses", [])
        if product.lifecycle_status not in allowed_statuses:
            allowed = False
            message = "Not available in current lifecycle phase"

    scan_event = log_event(
        db,
        qrcode_id=qrcode.id,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
        referer=request.headers.get("Referer"),
        geo=None,
        extra={"allowed": allowed},
    )

    log_qr_lifecycle_event(
        db,
        qrcode=qrcode,
        event_type="scan_recorded",
        metadata={"allowed": allowed, "scan_event_id": scan_event.id},
        commit=False,
    )

    if allowed:
        qr_crud.increment_reuse(db, qrcode=qrcode, commit=False)
    db.commit()
    db.refresh(qrcode)

    if allowed:
        redirect_url = qrcode.payload.get("redirect_url") if isinstance(qrcode.payload, dict) else None
        if redirect_url:
            return HTMLResponse(
                f"<html><head><meta http-equiv='refresh' content='0; url={redirect_url}' /></head><body>Redirecting...</body></html>"
            )
        return HTMLResponse("<h1>QR scan recorded</h1>")
    return HTMLResponse(f"<h1>QR not allowed: {message}</h1>", status_code=403)
