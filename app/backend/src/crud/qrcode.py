from __future__ import annotations

from sqlalchemy.orm import Session

from ..lifecycle.events import log_qr_lifecycle_event
from ..models.qrcode import QrCode
from ..schemas.qrcode import QrCreate, QrUpdate
from .base import CRUDBase


class CRUDQr(CRUDBase[QrCode, QrCreate, QrUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> QrCode | None:
        return db.query(QrCode).filter(QrCode.code == code).first()

    def increment_reuse(self, db: Session, *, qrcode: QrCode, commit: bool = True) -> QrCode:
        qrcode.reuse_count += 1
        db.add(qrcode)
        log_qr_lifecycle_event(
            db,
            qrcode=qrcode,
            event_type="reuse_incremented",
            metadata={"reuse_count": qrcode.reuse_count},
            commit=False,
        )
        if commit:
            db.commit()
            db.refresh(qrcode)
        else:
            db.flush()
        return qrcode


qr = CRUDQr(QrCode)
