"""Modelo ORM — Transaction (transacciones confirmadas para analítica).

Sprint 5 — EP-08: Gestión Avanzada de Pedidos.
HU 8.7: Dashboard Financiero con Rangos Temporales variables.

Almacena el detalle final de cada transacción completada, incluyendo
cantidad, descuentos aplicados y método de pago, para consultas de
agregación en el dashboard financiero del vendedor.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Transaction(Base):
    """Registro final de una transacción completada para analítica."""

    __tablename__ = "transactions"

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
    product_name: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="Snapshot del nombre del producto",
    )
    quantity: Mapped[int] = mapped_column(
        Integer,
        server_default="1",
    )
    unit_price_cop: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Precio unitario en COP al momento del cierre",
    )
    subtotal_cop: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="quantity × unit_price_cop",
    )
    discount_cop: Mapped[float] = mapped_column(
        Numeric(12, 2),
        server_default="0",
        comment="Descuento aplicado por cupón",
    )
    total_cop: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="subtotal - discount = total final",
    )
    payment_method: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="efectivo, nequi, daviplata",
    )
    coupon_code: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="Código del cupón aplicado (snapshot)",
    )
    buyer_note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Nota del comprador al realizar el pedido",
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    negotiation: Mapped["Negotiation"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<Transaction {self.id} — ${self.total_cop} COP>"
