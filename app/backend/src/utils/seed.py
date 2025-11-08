from __future__ import annotations

from sqlalchemy.orm import Session

from ..auth.security import get_password_hash
from ..models.customer import Customer
from ..models.product import Product
from ..models.qrcode import QrCode
from ..models.scanevent import ScanEvent
from ..models.user import User
from ..lifecycle.events import log_qr_lifecycle_event


def seed(db: Session) -> None:
    if db.query(User).first():
        return

    admin = User(email="admin@example.com", password_hash=get_password_hash("admin123"), role="admin")
    staff = User(email="staff@example.com", password_hash=get_password_hash("staff123"), role="staff")
    db.add_all([admin, staff])
    db.flush()

    customers = [
        Customer(name="Acme Corp", email="contact@acme.test", phone="123456789"),
        Customer(name="Globex", email="hello@globex.test", phone="987654321"),
    ]
    db.add_all(customers)
    db.flush()

    products = [
        Product(customer_id=customers[0].id, name="Widget", sku="WID-001", lifecycle_status="manufactured"),
        Product(customer_id=customers[0].id, name="Gadget", sku="GAD-002", lifecycle_status="in_store"),
        Product(customer_id=customers[1].id, name="Thing", sku="THI-003", lifecycle_status="sold"),
    ]
    db.add_all(products)
    db.flush()

    qrs = [
        QrCode(
            product_id=products[0].id,
            code="qr-unlimited-1",
            payload={"redirect_url": "https://example.com/widget"},
            reusable_mode="unlimited",
            reuse_limit=None,
            lifecycle_policy=None,
            created_by=admin.id,
        ),
        QrCode(
            product_id=products[0].id,
            code="qr-unlimited-2",
            payload={"redirect_url": "https://example.com/widget-manual"},
            reusable_mode="unlimited",
            reuse_limit=None,
            lifecycle_policy=None,
            created_by=admin.id,
        ),
        QrCode(
            product_id=products[1].id,
            code="qr-limited-1",
            payload={"redirect_url": "https://example.com/gadget"},
            reusable_mode="limited",
            reuse_limit=3,
            lifecycle_policy=None,
            created_by=admin.id,
        ),
        QrCode(
            product_id=products[1].id,
            code="qr-limited-2",
            payload={"redirect_url": "https://example.com/gadget-vip"},
            reusable_mode="limited",
            reuse_limit=3,
            lifecycle_policy=None,
            created_by=admin.id,
        ),
        QrCode(
            product_id=products[2].id,
            code="qr-phase-1",
            payload={"redirect_url": "https://example.com/thing"},
            reusable_mode="phase",
            reuse_limit=None,
            lifecycle_policy={"allowed_statuses": ["in_store", "sold"]},
            created_by=admin.id,
        ),
    ]
    db.add_all(qrs)
    db.flush()

    for qr in qrs:
        log_qr_lifecycle_event(
            db,
            qrcode=qr,
            event_type="created",
            actor_id=admin.id,
            metadata={"seed": True, "reusable_mode": qr.reusable_mode},
            lifecycle_state="issued",
            commit=False,
        )

    events = [
        ScanEvent(qrcode_id=qrs[0].id, ip="1.1.1.1"),
        ScanEvent(qrcode_id=qrs[1].id, ip="2.2.2.2"),
        ScanEvent(qrcode_id=qrs[2].id, ip="3.3.3.3"),
    ]
    db.add_all(events)
    db.commit()
