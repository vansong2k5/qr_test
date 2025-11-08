from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from ..models.qr_lifecycle_event import QrLifecycleEvent
from ..models.qrcode import QrCode


def log_qr_lifecycle_event(
    db: Session,
    *,
    qrcode: QrCode,
    event_type: str,
    actor_id: int | None = None,
    metadata: dict[str, Any] | None = None,
    lifecycle_state: str | None = None,
    commit: bool = False,
) -> QrLifecycleEvent:
    """Persist a lifecycle event for a QR code.

    Parameters
    ----------
    db:
        Active SQLAlchemy session.
    qrcode:
        QR code instance to associate the event with. The instance must be
        attached to the session.
    event_type:
        Name of the lifecycle event. Must be compatible with the
        ``qr_event_type`` enum in the database.
    actor_id:
        Optional user identifier responsible for the change.
    metadata:
        Optional JSON-serialisable metadata payload describing the event.
    lifecycle_state:
        When provided the QR code lifecycle_state will be updated as part of
        the same transaction. Timestamp helpers are handled automatically for
        ``active`` and terminal states.
    commit:
        When ``True`` the session will be committed and refreshed. The default
        is ``False`` so callers can bundle multiple writes in a single
        transaction.
    """

    metadata = metadata or {}
    event = QrLifecycleEvent(
        qrcode_id=qrcode.id,
        event_type=event_type,
        actor_id=actor_id,
        metadata=metadata,
        occurred_at=datetime.utcnow(),
    )

    if lifecycle_state:
        qrcode.lifecycle_state = lifecycle_state
        if lifecycle_state == "active" and qrcode.activated_at is None:
            qrcode.activated_at = datetime.utcnow()
        if lifecycle_state in {"retired", "recycled"}:
            qrcode.retired_at = datetime.utcnow()

    db.add(event)
    db.add(qrcode)

    if commit:
        db.commit()
        db.refresh(event)
        db.refresh(qrcode)
    else:
        db.flush()

    return event
