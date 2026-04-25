"""Modelo ORM — GmvMetric (registro de volumen bruto de mercancía).

HU 6.5: Registro automático del valor (GMV).
Se inserta un registro cuando una negociación cambia a estado 'completed',
almacenando el valor transaccional en COP para cálculo de métricas financieras.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GmvMetric(Base):
    """Registro individual de volumen transaccional bruto (GMV)."""

    __tablename__ = "gmv_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    negotiation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("negotiations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount_cop: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Valor de la transacción en COP al momento de la confirmación",
    )
    product_name: Mapped[str] = mapped_column(
        String(200),
        nullable=True,
        comment="Snapshot del nombre del producto al momento del cierre",
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<GmvMetric {self.id} — ${self.amount_cop} COP>"
