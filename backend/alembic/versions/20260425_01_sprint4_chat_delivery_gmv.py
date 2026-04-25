"""Sprint 4: Chat P2P, Confirmación de Entrega, y Métricas GMV.

Revision ID: 20260425_01
Revises: 20260409_01
Create Date: 2026-04-25

Cambios:
- Añade columnas buyer_confirmed, seller_confirmed, agreed_price_cop a negotiations.
- Crea tabla chat_messages para mensajes de chat persistentes (HU 6.1).
- Crea tabla gmv_metrics para registro de volumen transaccional (HU 6.5).
- Añade índices para optimizar consultas frecuentes.
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260425_01"
down_revision = "20260409_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Negotiations: nuevas columnas Sprint 4 (HU 6.4, 6.5) ---
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS buyer_confirmed BOOLEAN DEFAULT FALSE"
    )
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS seller_confirmed BOOLEAN DEFAULT FALSE"
    )
    op.execute(
        "ALTER TABLE negotiations ADD COLUMN IF NOT EXISTS agreed_price_cop NUMERIC(12,2)"
    )

    # --- Chat Messages (HU 6.1) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            negotiation_id UUID NOT NULL REFERENCES negotiations(id) ON DELETE CASCADE,
            sender_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chat_messages_negotiation
        ON chat_messages (negotiation_id, created_at ASC)
        """
    )

    # --- GMV Metrics (HU 6.5) ---
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS gmv_metrics (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            negotiation_id UUID NOT NULL UNIQUE REFERENCES negotiations(id) ON DELETE CASCADE,
            product_id UUID REFERENCES products(id) ON DELETE SET NULL,
            buyer_id UUID REFERENCES users(id) ON DELETE SET NULL,
            seller_id UUID REFERENCES users(id) ON DELETE SET NULL,
            amount_cop NUMERIC(12,2) NOT NULL,
            product_name VARCHAR(200),
            completed_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_gmv_metrics_completed_at
        ON gmv_metrics (completed_at DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_gmv_metrics_completed_at")
    op.execute("DROP TABLE IF EXISTS gmv_metrics")
    op.execute("DROP INDEX IF EXISTS idx_chat_messages_negotiation")
    op.execute("DROP TABLE IF EXISTS chat_messages")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS agreed_price_cop")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS seller_confirmed")
    op.execute("ALTER TABLE negotiations DROP COLUMN IF EXISTS buyer_confirmed")
