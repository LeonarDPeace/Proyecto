"""Modelo ORM — Coupon (cupones de descuento).

Sprint 5 — EP-08: Gestión Avanzada de Pedidos, Analítica y Refactorización UX.
HU 8.9: Sistema de Cupones de Descuento.

Permite a vendedores generar códigos de descuento (% o valor fijo en COP)
que se validan y aplican en el flujo de facturación del pedido (HU 8.4).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Coupon(Base):
    """Cupón de descuento creado por un vendedor."""

    __tablename__ = "coupons"
    __table_args__ = (
        CheckConstraint(
            "(discount_percent IS NOT NULL AND discount_fixed_cop IS NULL) "
            "OR (discount_percent IS NULL AND discount_fixed_cop IS NOT NULL)",
            name="ck_coupons_one_discount_type",
        ),
        CheckConstraint(
            "discount_percent IS NULL OR (discount_percent > 0 AND discount_percent <= 100)",
            name="ck_coupons_percent_range",
        ),
        CheckConstraint(
            "discount_fixed_cop IS NULL OR discount_fixed_cop > 0",
            name="ck_coupons_fixed_positive",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False,
        comment="Código alfanumérico del cupón (ej. VERA20)",
    )
    discount_percent: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="Descuento porcentual (1-100). Mutuamente excluyente con valor fijo.",
    )
    discount_fixed_cop: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Descuento en valor fijo COP. Mutuamente excluyente con porcentaje.",
    )
    max_uses: Mapped[int] = mapped_column(
        Integer,
        server_default="1",
        comment="Máximo de usos permitidos del cupón",
    )
    current_uses: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
    )
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    seller: Mapped["User"] = relationship()  # noqa: F821

    def is_valid(self) -> bool:
        """Verifica si el cupón es válido para uso."""
        if not self.is_active:
            return False
        if self.current_uses >= self.max_uses:
            return False
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return False
        return True

    def calculate_discount(self, subtotal: float) -> float:
        """Calcula el valor del descuento dado un subtotal."""
        if self.discount_percent:
            return round(subtotal * float(self.discount_percent) / 100, 2)
        if self.discount_fixed_cop:
            return min(float(self.discount_fixed_cop), subtotal)
        return 0.0

    def __repr__(self) -> str:
        dtype = f"{self.discount_percent}%" if self.discount_percent else f"${self.discount_fixed_cop} COP"
        return f"<Coupon {self.code} — {dtype}>"
