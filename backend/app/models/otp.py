"""Modelo ORM — OTPCode (códigos de un solo uso para autenticación).

HU 1.1: Inicio de sesión con OTP enviado al correo institucional.
Cada código tiene un TTL configurable y máximo 3 intentos de verificación.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OTPCode(Base):
    """Código de un solo uso para autenticación passwordless."""

    __tablename__ = "otp_codes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_used: Mapped[bool] = mapped_column(Boolean, server_default="false")
    attempts: Mapped[int] = mapped_column(Integer, server_default="0")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    def is_expired(self) -> bool:
        """Verifica si el OTP ha expirado."""
        return datetime.now(timezone.utc) > self.expires_at

    def is_valid(self) -> bool:
        """Verifica si el OTP es válido (no usado, no expirado, < 3 intentos)."""
        return not self.is_used and not self.is_expired() and self.attempts < 3

    def __repr__(self) -> str:
        return f"<OTPCode {self.email} expires={self.expires_at}>"
