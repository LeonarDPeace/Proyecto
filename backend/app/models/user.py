"""Modelo ORM — User (usuarios de la plataforma).

Cumple con Ley 1581/2012: campo accepted_terms_at obligatorio para operar.
Sprint 1: Autenticación OTP (sin contraseña). Privacy-first (HU 1.3).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Representa un usuario (vendedor o comprador) de VeraMarket."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    institutional_id: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    role: Mapped[str] = mapped_column(
        Enum("vendedor", "comprador", "admin", name="user_role", create_type=False),
        server_default="comprador",
    )
    vendor_status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "approved",
            "rejected",
            name="vendor_status_type",
            create_type=False,
        ),
        server_default="pending",
    )
    sinapsis_code: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )

    reputation: Mapped[float] = mapped_column(Numeric(3, 2), server_default="0.00")
    average_rating: Mapped[float] = mapped_column(
        Numeric(3, 2),
        server_default="0.00",
        comment="Promedio de calificaciones recibidas (1-5)",
    )
    total_reviews: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        comment="Número total de calificaciones recibidas",
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # --- Privacy settings (HU 1.3) ---
    show_email: Mapped[bool] = mapped_column(Boolean, server_default="false")
    show_phone: Mapped[bool] = mapped_column(Boolean, server_default="false")

    push_subscriptions: Mapped[list] = mapped_column(
        JSONB, server_default="'[]'::jsonb"
    )

    # Ley 1581/2012 — Consentimiento explícito de tratamiento de datos
    accepted_terms_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
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
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="seller", cascade="all, delete-orphan"
    )
    location: Mapped["Location | None"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    search_quotas: Mapped[list["UserSearchQuota"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.name} ({self.role})>"
