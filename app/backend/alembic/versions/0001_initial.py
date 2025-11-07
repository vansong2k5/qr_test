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
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.Enum("admin", "staff", name="user_role"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "customers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "lifecycle_status",
            sa.Enum(
                "manufactured",
                "in_warehouse",
                "in_store",
                "sold",
                "returned",
                "refurbished",
                "reused",
                "retired",
                name="lifecycle_status",
            ),
            nullable=False,
        ),
        sa.Column("meta", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "qrcodes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("code", sa.String(), nullable=False, unique=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("reusable_mode", sa.Enum("unlimited", "limited", "phase", name="reusable_mode"), nullable=False),
        sa.Column("reuse_limit", sa.Integer(), nullable=True),
        sa.Column("reuse_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lifecycle_policy", sa.JSON(), nullable=True),
        sa.Column("image_mask_path", sa.String(), nullable=True),
        sa.Column("image_render_path", sa.String(), nullable=True),
        sa.Column("image_svg_path", sa.String(), nullable=True),
        sa.Column("status", sa.Enum("active", "inactive", "revoked", name="qr_status"), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index("ix_qrcodes_code", "qrcodes", ["code"], unique=True)

    op.create_table(
        "scanevents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("qrcode_id", sa.Integer(), sa.ForeignKey("qrcodes.id"), nullable=False),
        sa.Column("scanned_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("ip", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("referer", sa.String(), nullable=True),
        sa.Column("geo_country", sa.String(), nullable=True),
        sa.Column("geo_city", sa.String(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("lon", sa.Float(), nullable=True),
        sa.Column("extra", sa.JSON(), nullable=True),
    )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("diff", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("scanevents")
    op.drop_index("ix_qrcodes_code", table_name="qrcodes")
    op.drop_table("qrcodes")
    op.drop_table("products")
    op.drop_table("customers")
    op.drop_table("users")
