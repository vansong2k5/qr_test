from __future__ import annotations

import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..crud.qrcode import qr as qr_crud
from ..deps import get_current_user, get_db, require_role
from ..models.product import Product
from ..models.qrcode import QrCode
from ..schemas.qrcode import QrOut, QrUpdate
from .service import create_qrcode
from ..lifecycle.events import log_qr_lifecycle_event

router = APIRouter()


@router.post("/generate", response_model=QrOut)
async def generate_qr(
    product_id: int = Form(...),
    reusable_mode: str = Form(...),
    payload: str = Form("{}"),
    reuse_limit: int | None = Form(None),
    lifecycle_policy: str | None = Form(None),
    error_correction: str = Form("H"),
    foreground: str = Form("#000000"),
    background: str = Form("#FFFFFF"),
    mask_image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    user=Depends(require_role("admin")),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    payload_data = json.loads(payload or "{}")
    lifecycle_data = json.loads(lifecycle_policy) if lifecycle_policy else None
    mask_bytes = await mask_image.read() if mask_image else None
    qrcode = create_qrcode(
        db,
        product_id=product_id,
        payload=payload_data,
        reusable_mode=reusable_mode,
        reuse_limit=reuse_limit,
        lifecycle_policy=lifecycle_data,
        mask_bytes=mask_bytes,
        created_by=user.id,
        options={"error_correction": error_correction, "foreground": foreground, "background": background},
    )
    return qrcode


@router.get("/", response_model=list[QrOut])
async def list_qrcodes(
    status: str | None = None,
    product_id: int | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = db.query(QrCode).order_by(QrCode.created_at.desc())
    if status:
        query = query.filter(QrCode.status == status)
    if product_id:
        query = query.filter(QrCode.product_id == product_id)
    return query.limit(100).all()


@router.get("/{qr_id}", response_model=QrOut)
async def get_qrcode(qr_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    qrcode = qr_crud.get(db, id=qr_id)
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    return qrcode


@router.put("/{qr_id}", response_model=QrOut)
async def update_qrcode(qr_id: int, payload: QrUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    qrcode = qr_crud.get(db, id=qr_id)
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(qrcode, field, value)
    db.add(qrcode)
    db.flush()
    log_qr_lifecycle_event(
        db,
        qrcode=qrcode,
        event_type="updated",
        actor_id=user.id,
        metadata=update_data,
        lifecycle_state=update_data.get("lifecycle_state"),
        commit=False,
    )
    db.commit()
    db.refresh(qrcode)
    return qrcode


@router.delete("/{qr_id}", status_code=204)
async def delete_qrcode(qr_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    qrcode = qr_crud.get(db, id=qr_id)
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    qr_crud.remove(db, id=qr_id)
    return None


@router.post("/{qr_id}/revoke", response_model=QrOut)
async def revoke_qrcode(qr_id: int, db: Session = Depends(get_db), user=Depends(require_role("admin"))):
    qrcode = qr_crud.get(db, id=qr_id)
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    if qrcode.status == "revoked":
        return qrcode
    qrcode.status = "revoked"
    db.add(qrcode)
    db.flush()
    log_qr_lifecycle_event(
        db,
        qrcode=qrcode,
        event_type="revoked",
        actor_id=user.id,
        metadata={"reason": "manual"},
        lifecycle_state="retired",
        commit=False,
    )
    db.commit()
    db.refresh(qrcode)
    return qrcode
