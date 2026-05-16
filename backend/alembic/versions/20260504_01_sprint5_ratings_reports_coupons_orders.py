"""Sprint 5: Ratings, Reports, Transactions, Coupons, Pedidos Avanzados.

Revision ID: 20260504_01
Revises: 20260425_01
Create Date: 2026-05-04

Cambios:
- Amplía negotiation_status_enum con 'paused', 'cancelled', 'delivered'.
- Añade report_reason_enum ('spam', 'offensive', 'fraud').
- Añade columnas a negotiations: quantity, buyer_note, payment_method,
  coupon_code, transaction_locked (HU 8.1, 8.3, 8.4, 8.5).
- Añade columnas a users: average_rating, total_reviews (HU 7.2).
- Crea tabla ratings (HU 7.1).
- Crea tabla reports (HU 7.3).
- Crea tabla transactions (HU 8.7).
- Crea tabla coupons (HU 8.9).
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260504_01"
down_revision = "20260425_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Ampliar negotiation_status_enum ---
    op.execute("ALTER TYPE negotiation_status_enum ADD VALUE IF NOT EXISTS 'paused'")
    op.execute("ALTER TYPE negotiation_status_enum ADD VALUE IF NOT EXISTS 'cancelled'")
    op.execute("ALTER TYPE negotiation_status_enum ADD VALUE IF NOT EXISTS 'delivered'")

    # --- Crear report_reason_enum ---
    op.execute(
        """
        DO $$ BEGIN
            CREATE TYPE report_reason_enum AS ENUM ('spam', 'offensive', 'fraud');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$
        """
    )

    # --- Negotiations: nuevas columnas Sprint 5 ---
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1"
    )
    op.execute("ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS buyer_note TEXT")
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS payment_method VARCHAR(30)"
    )
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS coupon_code VARCHAR(30)"
    )
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS transaction_locked BOOLEAN DEFAULT FALSE"
    )

    # --- Users: campos de reputación (HU 7.2) ---
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS average_rating NUMERIC(3,2) DEFAULT 0.00"
    )
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS total_reviews INTEGER DEFAULT 0"
    )

    # --- Ratings (HU 7.1) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ratings (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            negotiation_id UUID NOT NULL REFERENCES negotiations(id) ON DELETE CASCADE,
            reviewer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reviewed_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            stars INTEGER NOT NULL CHECK (stars >= 1 AND stars <= 5),
            comment TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_ratings_one_review_per_user UNIQUE (negotiation_id, reviewer_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_ratings_reviewed_id ON ratings (reviewed_id)"
    )

    # --- Reports (HU 7.3) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            reporter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reported_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            reason report_reason_enum NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_reports_one_per_user_product UNIQUE (reporter_id, product_id),
            CONSTRAINT ck_reports_no_self_report CHECK (reporter_id != reported_user_id)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_reports_product_id ON reports (product_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_reports_status ON reports (status)")

    # --- Transactions (HU 8.7) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            negotiation_id UUID NOT NULL UNIQUE REFERENCES negotiations(id) ON DELETE CASCADE,
            product_id UUID REFERENCES products(id) ON DELETE SET NULL,
            buyer_id UUID REFERENCES users(id) ON DELETE SET NULL,
            seller_id UUID REFERENCES users(id) ON DELETE SET NULL,
            product_name VARCHAR(200),
            quantity INTEGER DEFAULT 1,
            unit_price_cop NUMERIC(12,2) NOT NULL,
            subtotal_cop NUMERIC(12,2) NOT NULL,
            discount_cop NUMERIC(12,2) DEFAULT 0,
            total_cop NUMERIC(12,2) NOT NULL,
            payment_method VARCHAR(30),
            coupon_code VARCHAR(30),
            buyer_note TEXT,
            completed_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_seller_id ON transactions (seller_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_transactions_completed_at ON transactions (completed_at)"
    )

    # --- Coupons (HU 8.9) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS coupons (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            seller_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            code VARCHAR(30) NOT NULL UNIQUE,
            discount_percent NUMERIC(5,2),
            discount_fixed_cop NUMERIC(12,2),
            max_uses INTEGER DEFAULT 1,
            current_uses INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            expires_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT ck_coupons_one_discount_type
                CHECK ((discount_percent IS NOT NULL AND discount_fixed_cop IS NULL)
                    OR (discount_percent IS NULL AND discount_fixed_cop IS NOT NULL)),
            CONSTRAINT ck_coupons_percent_range
                CHECK (discount_percent IS NULL OR (discount_percent > 0 AND discount_percent <= 100)),
            CONSTRAINT ck_coupons_fixed_positive
                CHECK (discount_fixed_cop IS NULL OR discount_fixed_cop > 0)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_coupons_seller_id ON coupons (seller_id)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_coupons_code ON coupons (code)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_coupons_code")
    op.execute("DROP INDEX IF EXISTS idx_coupons_seller_id")
    op.execute("DROP TABLE IF EXISTS coupons")
    op.execute("DROP INDEX IF EXISTS idx_transactions_completed_at")
    op.execute("DROP INDEX IF EXISTS idx_transactions_seller_id")
    op.execute("DROP TABLE IF EXISTS transactions")
    op.execute("DROP INDEX IF EXISTS idx_reports_status")
    op.execute("DROP INDEX IF EXISTS idx_reports_product_id")
    op.execute("DROP TABLE IF EXISTS reports")
    op.execute("DROP INDEX IF EXISTS idx_ratings_reviewed_id")
    op.execute("DROP TABLE IF EXISTS ratings")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS total_reviews")
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS average_rating")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS transaction_locked")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS coupon_code")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS payment_method")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS buyer_note")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS quantity")
    # Note: Cannot easily remove enum values in PostgreSQL; leave them.
