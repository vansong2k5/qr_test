from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.qrcode import QrCode
from app.models.reuse_history import ReuseHistory
from app.schemas.qrcode import QrOptions
from app.storage.local import storage
from app.utils.qr_renderer import ImageMaskQrRenderer


def _serialize_data(data: dict | str) -> tuple[dict | None, str | None]:
    if isinstance(data, dict):
        return data, None
    if data.startswith("http://") or data.startswith("https://"):
        return None, data
    try:
        parsed = json.loads(data)
        if isinstance(parsed, dict):
            return parsed, None
    except json.JSONDecodeError:
        pass
    return None, data


def create_qrcode(
    db: Session,
    *,
    product_id: int | None,
    customer_id: int | None,
    data: dict | str,
    reuse_allowed: bool,
    options: QrOptions,
    mask_file: UploadFile | None,
    logo_file: UploadFile | None,
) -> QrCode:
    mask_bytes = mask_file.file.read() if mask_file else None
    logo_bytes = logo_file.file.read() if logo_file else None

    if logo_bytes and options.ecc != "H":
        # Chèn logo cần ECC cao hơn để che bớt module nhưng vẫn đọc được
        options.ecc = "H"

    renderer = ImageMaskQrRenderer(
        data=json.dumps(data) if isinstance(data, dict) else str(data),
        ecc=options.ecc,
        fg_color=options.fg_color,
        bg_color=options.bg_color,
        margin=options.margin,
        size=options.size,
        mask_bytes=mask_bytes,
        logo_bytes=logo_bytes if options.logo_enabled else None,
        threshold=options.threshold,
    )

    result = renderer.render()

    data_json, data_url = _serialize_data(data)

    qrcode = QrCode(
        id=result.code_id,
        product_id=product_id,
        customer_id=customer_id,
        data_json=data_json,
        data_url=data_url,
        reuse_allowed=reuse_allowed,
        reuse_cycle=0,
        active=True,
        version=result.version,
        ecc=result.ecc,
        image_path_png=result.png_path,
        image_path_svg=result.svg_path,
        mask_path=result.mask_path,
        logo_path=result.logo_path,
    )
    db.add(qrcode)
    db.commit()
    db.refresh(qrcode)
    return qrcode


def start_reuse_cycle(db: Session, code_id: uuid.UUID, reason: str, note: str | None) -> QrCode:
    qrcode = db.query(QrCode).filter(QrCode.id == code_id).first()
    if not qrcode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QR not found")
    if not qrcode.reuse_allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="QR không cho phép tái sử dụng")
    qrcode.reuse_cycle += 1
    history = ReuseHistory(code_id=qrcode.id, cycle=qrcode.reuse_cycle, reason=reason, note=note)
    db.add(history)
    db.add(qrcode)
    db.commit()
    db.refresh(qrcode)
    return qrcode


def build_qr_response(qrcode: QrCode) -> dict[str, Any]:
    return {
        "code_id": qrcode.id,
        "product_id": qrcode.product_id,
        "customer_id": qrcode.customer_id,
        "reuse_allowed": qrcode.reuse_allowed,
        "reuse_cycle": qrcode.reuse_cycle,
        "active": qrcode.active,
        "version": qrcode.version,
        "ecc": qrcode.ecc,
        "image_url_png": storage.url_for(qrcode.image_path_png),
        "image_url_svg": storage.url_for(qrcode.image_path_svg),
        "created_at": qrcode.created_at,
        "updated_at": qrcode.updated_at,
    }
