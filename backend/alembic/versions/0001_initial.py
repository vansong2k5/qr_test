"""initial schema"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255)),
        sa.Column("phone", sa.String(length=50)),
        sa.Column("meta", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sku", sa.String(length=100), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1024)),
        sa.Column("owner_customer_id", sa.Integer(), sa.ForeignKey("customers.id")),
        sa.Column("meta", sa.JSON(), server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "webhooks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("target_url", sa.String(length=512), nullable=False),
        sa.Column("event", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key_hash", sa.String(length=255), nullable=False, unique=True),
        sa.Column("label", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "qrcodes",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id")),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id")),
        sa.Column("data_json", sa.JSON()),
        sa.Column("data_url", sa.Text()),
        sa.Column("reuse_allowed", sa.Boolean(), server_default=sa.false()),
        sa.Column("reuse_cycle", sa.Integer(), server_default="0"),
        sa.Column("active", sa.Boolean(), server_default=sa.true()),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("ecc", sa.String(length=2), server_default="H"),
        sa.Column("image_path_png", sa.String(length=255), nullable=False),
        sa.Column("image_path_svg", sa.String(length=255), nullable=False),
        sa.Column("mask_path", sa.String(length=255)),
        sa.Column("logo_path", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    op.create_table(
        "scan_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code_id", sa.String(length=36), sa.ForeignKey("qrcodes.id")),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ip", sa.String(length=64)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("referer", sa.Text()),
        sa.Column("approx_geo", sa.String(length=255)),
        sa.Column("device", sa.String(length=50)),
        sa.Column("reuse_cycle_at_scan", sa.Integer(), server_default="0"),
    )

    op.create_table(
        "reuse_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code_id", sa.String(length=36), sa.ForeignKey("qrcodes.id")),
        sa.Column("cycle", sa.Integer(), server_default="0"),
        sa.Column("reason", sa.String(length=255)),
        sa.Column("note", sa.Text()),
        sa.Column("ts", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("reuse_history")
    op.drop_table("scan_events")
    op.drop_table("qrcodes")
    op.drop_table("api_keys")
    op.drop_table("webhooks")
    op.drop_table("products")
    op.drop_table("customers")
    op.drop_table("users")
