from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.product import Product
from ..schemas.product import ProductCreate, ProductUpdate
from .base import CRUDBase


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def filter_by_status(
        self, db: Session, *, status: str | None = None, skip: int = 0, limit: int = 100
    ):
        q = db.query(Product)
        if status:
            q = q.filter(Product.lifecycle_status == status)
        return q.offset(skip).limit(limit).all()


product = CRUDProduct(Product)
