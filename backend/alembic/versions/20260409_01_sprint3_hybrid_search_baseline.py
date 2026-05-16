"""Sprint 3 baseline: soft-delete consistency and daily search quotas.

Revision ID: 20260409_01
Revises:
Create Date: 2026-04-09
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260409_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS user_search_quotas (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            search_date DATE NOT NULL,
            searches_used INTEGER NOT NULL DEFAULT 0,
            daily_limit INTEGER NOT NULL DEFAULT 10,
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            CONSTRAINT uq_user_search_quota_user_day UNIQUE (user_id, search_date)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_user_search_quotas_user_day
        ON user_search_quotas (user_id, search_date)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_user_search_quotas_user_day")
    op.execute("DROP TABLE IF EXISTS user_search_quotas")
    # Keep column drop conditional to avoid errors if table was rebuilt from init.sql.
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS is_deleted")
