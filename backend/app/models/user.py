"""Modelo ORM — User (usuarios de la plataforma).

Cumple con Ley 1581/2012: campo accepted_terms_at obligatorio para operar.
Correos validados contra dominio .edu.co (institucional).
Sprint 1: Autenticación OTP (sin contraseña). Privacy-first (HU 1.3).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    """Representa un usuario (vendedor o comprador) de VeraMarket."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "email ~* '^.+\\.edu\\.co$'",
            name="ck_users_email_edu_co",
        ),
    )

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
        Enum("vendedor", "comprador", name="user_role_enum", create_type=False),
        server_default="comprador",
    )
    reputation: Mapped[float] = mapped_column(
        Numeric(3, 2), server_default="0.00"
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # --- Privacy settings (HU 1.3) ---
    show_email: Mapped[bool] = mapped_column(Boolean, server_default="false")
    show_phone: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Ley 1581/2012 — Consentimiento explícito de tratamiento de datos
    accepted_terms_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # --- Relationships ---
    products: Mapped[list["Product"]] = relationship(  # noqa: F821
        back_populates="seller", cascade="all, delete-orphan"
    )
    location: Mapped["Location | None"] = relationship(  # noqa: F821
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User {self.name} ({self.role})>"
