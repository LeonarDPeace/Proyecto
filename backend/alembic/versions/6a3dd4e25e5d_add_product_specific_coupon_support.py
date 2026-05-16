"""Add product-specific coupon support

Revision ID: 6a3dd4e25e5d
Revises: 20260509_01
Create Date: 2026-05-09 08:47:21.916532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6a3dd4e25e5d'
down_revision: Union[str, None] = '20260509_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('coupon_products',
    sa.Column('coupon_id', sa.Uuid(), nullable=False),
    sa.Column('product_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['coupon_id'], ['coupons.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('coupon_id', 'product_id')
    )


def downgrade() -> None:
    op.drop_table('coupon_products')
