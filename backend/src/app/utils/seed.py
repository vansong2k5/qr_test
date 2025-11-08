from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models import Customer, Product, User
from app.schemas.qrcode import QrOptions
from app.services.qr_service import create_qrcode


def seed(db: Session) -> None:
    if db.query(User).count():
        return
    admin = User(email="admin@example.com", password_hash=get_password_hash("admin123"), role="admin")
    db.add(admin)
    customer = Customer(name="Công ty ABC", email="contact@abc.com")
    db.add(customer)
    db.commit()
    db.refresh(admin)
    db.refresh(customer)

    product1 = Product(sku="SKU-001", name="Sản phẩm A", owner_customer_id=customer.id)
    product2 = Product(sku="SKU-002", name="Sản phẩm B", owner_customer_id=customer.id)
    db.add_all([product1, product2])
    db.commit()
    db.refresh(product1)
    db.refresh(product2)

    options = QrOptions()
    data = {"product": product1.name, "sku": product1.sku}
    create_qrcode(
        db,
        product_id=product1.id,
        customer_id=customer.id,
        data=data,
        reuse_allowed=True,
        options=options,
        mask_file=None,
        logo_file=None,
    )
