from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_qr_lifecycle"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    qr_lifecycle_state = sa.Enum(
        "issued",
        "active",
        "suspended",
        "retired",
        "recycled",
        name="qr_lifecycle_state",
    )
    qr_lifecycle_state.create(op.get_bind(), checkfirst=True)

    qr_event_type = sa.Enum(
        "created",
        "updated",
        "status_changed",
        "scan_recorded",
        "reuse_incremented",
        "revoked",
        "activated",
        "retired",
        "esg_tagged",
        name="qr_event_type",
    )
    qr_event_type.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "qrcodes",
        sa.Column("lifecycle_state", qr_lifecycle_state, nullable=False, server_default="issued"),
    )
    op.add_column("qrcodes", sa.Column("activated_at", sa.DateTime(), nullable=True))
    op.add_column("qrcodes", sa.Column("retired_at", sa.DateTime(), nullable=True))

    op.create_table(
        "qr_lifecycle_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qrcode_id", sa.Integer(), sa.ForeignKey("qrcodes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", qr_event_type, nullable=False),
        sa.Column("occurred_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
    )
    op.create_index(
        "ix_qr_lifecycle_events_qrcode_id",
        "qr_lifecycle_events",
        ["qrcode_id"],
    )

    op.alter_column("qrcodes", "lifecycle_state", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_qr_lifecycle_events_qrcode_id", table_name="qr_lifecycle_events")
    op.drop_table("qr_lifecycle_events")
    op.drop_column("qrcodes", "retired_at")
    op.drop_column("qrcodes", "activated_at")
    op.drop_column("qrcodes", "lifecycle_state")

    qr_event_type = sa.Enum(name="qr_event_type")
    qr_event_type.drop(op.get_bind(), checkfirst=True)

    qr_lifecycle_state = sa.Enum(name="qr_lifecycle_state")
    qr_lifecycle_state.drop(op.get_bind(), checkfirst=True)
