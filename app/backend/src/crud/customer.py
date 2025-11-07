from __future__ import annotations

from sqlalchemy.orm import Session

from ..models.customer import Customer
from ..schemas.customer import CustomerCreate, CustomerUpdate
from .base import CRUDBase


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def search(self, db: Session, *, query: str, skip: int = 0, limit: int = 100):
        q = db.query(Customer)
        if query:
            like = f"%{query}%"
            q = q.filter(Customer.name.ilike(like) | Customer.email.ilike(like))
        return q.offset(skip).limit(limit).all()


customer = CRUDCustomer(Customer)
