from __future__ import annotations

import json

from sqlalchemy.orm import Session

from typing import Any

from ..models.qrcode import QrCode
from ..qr.render import render_qr
from ..lifecycle.events import log_qr_lifecycle_event


def create_qrcode(
    db: Session,
    *,
    product_id: int,
    payload: dict[str, Any] | None,
    reusable_mode: str,
    reuse_limit: int | None,
    lifecycle_policy: dict[str, Any] | None,
    mask_bytes: bytes | None,
    created_by: int,
    options: dict[str, Any] | None = None,
) -> QrCode:
    data = json.dumps(payload or {})
    render_result = render_qr(
        data,
        mask_bytes=mask_bytes,
        foreground=(options or {}).get("foreground", "#000000"),
        background=(options or {}).get("background", "#FFFFFF"),
        error_correction=(options or {}).get("error_correction", "H"),
    )
    qrcode = QrCode(
        product_id=product_id,
        code=render_result.code,
        payload=payload or {},
        reusable_mode=reusable_mode,
        reuse_limit=reuse_limit,
        lifecycle_policy=lifecycle_policy,
        image_mask_path=render_result.mask_path,
        image_render_path=render_result.png_path,
        image_svg_path=render_result.svg_path,
        created_by=created_by,
    )
    db.add(qrcode)
    db.flush()
    log_qr_lifecycle_event(
        db,
        qrcode=qrcode,
        event_type="created",
        actor_id=created_by,
        metadata={
            "reusable_mode": reusable_mode,
            "reuse_limit": reuse_limit,
            "lifecycle_policy": lifecycle_policy or {},
        },
        lifecycle_state="issued",
        commit=False,
    )
    db.commit()
    db.refresh(qrcode)
    return qrcode
