from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.qrcode import QrCode
from ..schemas.qrcode import QrCreate, QrUpdate
from .base import CRUDBase


class CRUDQr(CRUDBase[QrCode, QrCreate, QrUpdate]):
    def get_by_code(self, db: Session, *, code: str) -> QrCode | None:
        return db.query(QrCode).filter(QrCode.code == code).first()

    def increment_reuse(self, db: Session, *, qrcode: QrCode) -> QrCode:
        qrcode.reuse_count += 1
        db.add(qrcode)
        db.commit()
        db.refresh(qrcode)
        return qrcode


qr = CRUDQr(QrCode)
