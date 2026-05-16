"""Add advanced e-commerce fields to products.

Revision ID: 20260507_02
Revises: 20260507_01
Create Date: 2026-05-07

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260507_02"
down_revision = "20260507_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Crear fulfillment_type enum ---
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE fulfillment_type AS ENUM ('merchant', 'veramarket');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
        """
    )

    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS stock INTEGER DEFAULT 1"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS discount_percentage NUMERIC(5, 2) DEFAULT 0.00"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS warranty_days INTEGER DEFAULT 0"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_returnable BOOLEAN DEFAULT false"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS fulfillment_type fulfillment_type DEFAULT 'merchant'"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS payment_methods JSONB DEFAULT '[\"efectivo\", \"transferencia\"]'::jsonb"
    )
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS promotions JSONB DEFAULT '[]'::jsonb"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS promotions")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS payment_methods")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS fulfillment_type")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS is_returnable")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS warranty_days")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS discount_percentage")
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS stock")
