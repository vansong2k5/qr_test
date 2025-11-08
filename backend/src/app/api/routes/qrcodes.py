from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import String, cast
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db_session
from app.models.qrcode import QrCode
from app.models.reuse_history import ReuseHistory
from app.schemas.qrcode import QrOptions, QrOut, QrUpdateRequest, ReuseHistoryOut, ReuseStartRequest
from app.services.qr_service import build_qr_response, create_qrcode, start_reuse_cycle
from app.utils.qr_renderer import decode_qr_image

router = APIRouter()


@router.post("/generate", response_model=QrOut)
async def generate_qrcode(
    data: str = Form(...),
    product_id: int | None = Form(None),
    customer_id: int | None = Form(None),
    reuse_allowed: bool = Form(False),
    options: str | None = Form(None),
    mask_image: UploadFile | None = File(None),
    logo_image: UploadFile | None = File(None),
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    options_obj = QrOptions.parse_raw(options) if options else QrOptions()
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        payload = data
    qrcode = create_qrcode(
        db,
        product_id=product_id,
        customer_id=customer_id,
        data=payload,
        reuse_allowed=reuse_allowed,
        options=options_obj,
        mask_file=mask_image,
        logo_file=logo_image,
    )
    return build_qr_response(qrcode)


@router.get("/", response_model=list[QrOut])
async def list_qrcodes(
    query: str | None = None,
    active: bool | None = None,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    qs = db.query(QrCode)
    if query:
        qs = qs.filter(cast(QrCode.id, String).ilike(f"%{query}%"))
    if active is not None:
        qs = qs.filter(QrCode.active == active)
    qrcodes = qs.order_by(QrCode.created_at.desc()).limit(100).all()
    return [build_qr_response(qr) for qr in qrcodes]


@router.get("/{code_id}", response_model=QrOut)
async def get_qrcode(code_id: uuid.UUID, db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    qrcode = db.query(QrCode).filter(QrCode.id == code_id).first()
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    return build_qr_response(qrcode)


@router.patch("/{code_id}", response_model=QrOut)
async def update_qrcode(
    code_id: uuid.UUID,
    payload: QrUpdateRequest,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    qrcode = db.query(QrCode).filter(QrCode.id == code_id).first()
    if not qrcode:
        raise HTTPException(status_code=404, detail="QR not found")
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(qrcode, field, value)
    db.add(qrcode)
    db.commit()
    db.refresh(qrcode)
    return build_qr_response(qrcode)


@router.post("/{code_id}/reuse/start", response_model=QrOut)
async def start_reuse(
    code_id: uuid.UUID,
    payload: ReuseStartRequest,
    db: Session = Depends(get_db_session),
    user=Depends(get_current_user),
):
    qrcode = start_reuse_cycle(db, code_id, payload.reason, payload.note)
    return build_qr_response(qrcode)


@router.get("/{code_id}/reuse/history", response_model=list[ReuseHistoryOut])
async def reuse_history(
    code_id: uuid.UUID, db: Session = Depends(get_db_session), user=Depends(get_current_user)
):
    history = (
        db.query(ReuseHistory)
        .filter(ReuseHistory.code_id == code_id)
        .order_by(ReuseHistory.ts.desc())
        .all()
    )
    return history


@router.post("/test-decode", response_model=dict)
async def test_decode(image: UploadFile = File(...)):
    data = image.file.read()
    decoded = decode_qr_image(data)
    return {"decoded": decoded}
