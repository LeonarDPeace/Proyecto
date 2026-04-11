"""Modelo ORM — Negotiation (negociaciones P2P entre compradores y vendedores).

Controla el flujo de privacidad: solo al alcanzar status 'accepted'
se revelan datos de contacto (email, phone) — cumplimiento Ley 1581/2012.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<Negotiation {self.id} — {self.status}>"
