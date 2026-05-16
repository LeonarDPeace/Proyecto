"""Add last_active_at to users.

Revision ID: 20260507_01
Revises: 20260504_01
Create Date: 2026-05-07

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260507_01"
down_revision = "20260504_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_active_at TIMESTAMPTZ"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE users DROP COLUMN IF EXISTS last_active_at")
