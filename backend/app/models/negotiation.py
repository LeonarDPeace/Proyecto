"""Modelo ORM — Negotiation (negociaciones P2P entre compradores y vendedores).

Sprint 4 — EP-06: Negociación y Cierre P2P (Frictionless).
HU 6.1: Chat interno en tiempo real (relationship con ChatMessage).
HU 6.4: Marcado manual de "Transacción Completada" (ambas partes confirman).
HU 6.5: Registro automático del valor (GMV).

Controla el flujo de privacidad: solo al alcanzar status 'accepted'
se revelan datos de contacto (email, phone) — cumplimiento Ley 1581/2012.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Negotiation(Base):
    """Representa una negociación entre un comprador y un vendedor."""

    __tablename__ = "negotiations"
    __table_args__ = (
        CheckConstraint(
            "buyer_id != seller_id",
            name="ck_negotiations_no_self_deal",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "accepted",
            "rejected",
            "completed",
            name="negotiation_status_enum",
            create_type=False,
        ),
        server_default="pending",
    )

    # --- HU 6.4: Marcado manual de "Transacción Completada" ---
    # Ambas partes deben confirmar para que la transacción se complete.
    buyer_confirmed: Mapped[bool] = mapped_column(
        Boolean, server_default="false"
    )
    seller_confirmed: Mapped[bool] = mapped_column(
        Boolean, server_default="false"
    )

    # --- HU 6.5: Valor transaccional (snapshot del precio al aceptar) ---
    agreed_price_cop: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Precio acordado en COP (snapshot del precio del producto)",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    buyer: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[buyer_id]
    )
    seller: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[seller_id]
    )
    product: Mapped["Product"] = relationship()  # noqa: F821
    messages: Mapped[list["ChatMessage"]] = relationship(  # noqa: F821
        back_populates="negotiation",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )

    def __repr__(self) -> str:
        return f"<Negotiation {self.id} — {self.status}>"
