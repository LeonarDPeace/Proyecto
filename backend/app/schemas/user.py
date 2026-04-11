"""Esquemas Pydantic — User (Sprint 1).

Separa la información pública de la privada (Ley 1581/2012).
HU 1.3: Los campos email/phone solo se muestran si el usuario lo permite.
"""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Campos comunes de usuario."""

    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    institutional_id: str = Field(..., min_length=1, max_length=50)
    role: str = Field(default="comprador", pattern="^(vendedor|comprador)$")


class UserCreate(UserBase):
    """Datos requeridos para crear un usuario (registro OTP)."""

    phone: str | None = Field(default=None, max_length=20)
    accept_terms: bool = Field(
        ..., description="Aceptación explícita de T&C (Ley 1581/2012)"
    )

    @field_validator("accept_terms")
    @classmethod
    def must_accept_terms(cls, v: bool) -> bool:
        """El usuario debe aceptar los términos para registrarse."""
        if not v:
            msg = "Debe aceptar los términos y condiciones (Ley 1581/2012)"
            raise ValueError(msg)
        return v


class UserPublic(BaseModel):
    """Datos públicos de un usuario (sin info sensible por defecto).

    HU 1.3: email y phone solo se incluyen si show_email/show_phone están activos.
    """

    id: uuid.UUID
    name: str
    role: str
    reputation: float
    is_verified: bool
    # Campos opcionales — solo presentes si la privacidad lo permite
    email: EmailStr | None = None
    phone: str | None = None

    model_config = {"from_attributes": True}


class UserPrivate(BaseModel):
    """Datos completos — solo visibles al propio usuario.

    Incluye toda la información sensible + configuración de privacidad.
    """

    id: uuid.UUID
    name: str
    email: EmailStr
    phone: str | None
    institutional_id: str
    role: str
    reputation: float
    is_verified: bool
    show_email: bool
    show_phone: bool
    accepted_terms_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSearchQuotaRead(BaseModel):
    """Estado de cuota diaria para búsquedas inteligentes."""

    business_date: date
    daily_limit: int
    searches_used: int
    remaining: int
