"""Modelo ORM — Report (reportes de comportamiento indebido).

Sprint 5 — EP-07: Moderación y Reputación Comunitaria.
HU 7.3: Sistema de reporte por comportamiento indebido.

Permite a los usuarios denunciar productos o perfiles que incumplan
las normas de la comunidad. Si un producto acumula un umbral de
reportes, el sistema lo oculta automáticamente (is_active=false)
hasta que un administrador lo revise.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

# Umbral de reportes para auto-ocultamiento de un producto.
AUTO_HIDE_THRESHOLD = 3


class Report(Base):
    """Reporte de comportamiento indebido sobre un producto o usuario."""

    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint(
            "reporter_id",
            "product_id",
            name="uq_reports_one_per_user_product",
        ),
        CheckConstraint(
            "reporter_id != reported_user_id",
            name="ck_reports_no_self_report",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    reporter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que emite el reporte",
    )
    reported_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario propietario del producto reportado",
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=True,
        comment="Producto reportado (opcional si es reporte de usuario)",
    )
    reason: Mapped[str] = mapped_column(
        Enum(
            "spam",
            "offensive",
            "fraud",
            name="report_reason_enum",
            create_type=False,
        ),
        nullable=False,
        comment="Razón del reporte: spam, offensive, fraud",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Descripción adicional opcional del reporte",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="pending",
        comment="pending, reviewed, dismissed",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    reporter: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[reporter_id],
    )
    reported_user: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[reported_user_id],
    )
    product: Mapped["Product"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<Report {self.id} — {self.reason} on product {self.product_id}>"
