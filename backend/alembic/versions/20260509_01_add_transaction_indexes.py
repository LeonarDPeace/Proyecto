"""Add transaction indexes for analytics.

Revision ID: 20260509_01
Revises: 20260507_02
Create Date: 2026-05-09

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20260509_01"
down_revision = "20260507_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Add indexes to transactions table ---
    op.create_index(
        "ix_transactions_seller_id",
        "transactions",
        ["seller_id"],
        unique=False
    )
    op.create_index(
        "ix_transactions_completed_at",
        "transactions",
        ["completed_at"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_completed_at", table_name="transactions")
    op.drop_index("ix_transactions_seller_id", table_name="transactions")
