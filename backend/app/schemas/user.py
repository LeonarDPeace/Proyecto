"""Esquemas Pydantic — User.

Separa la información pública de la privada (Ley 1581/2012).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Campos comunes de usuario."""

    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    institutional_id: str = Field(..., min_length=1, max_length=50)
    role: str = Field(default="comprador", pattern="^(vendedor|comprador)$")

    @field_validator("email")
    @classmethod
    def validate_institutional_email(cls, v: str) -> str:
        """El correo debe pertenecer a un dominio institucional .edu.co."""
        if not v.strip().lower().endswith(".edu.co"):
            msg = "Solo se permiten correos institucionales (.edu.co)"
            raise ValueError(msg)
        return v.strip().lower()


class UserCreate(UserBase):
    """Datos requeridos para crear un usuario."""

    password: str = Field(..., min_length=8, max_length=128)
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
    """Datos públicos de un usuario (sin info sensible)."""

    id: uuid.UUID
    name: str
    role: str
    reputation: float
    is_verified: bool

    model_config = {"from_attributes": True}


class UserPrivate(UserPublic):
    """Datos completos — solo visibles al propio usuario o con negociación aceptada."""

    email: EmailStr
    phone: str | None
    institutional_id: str
    accepted_terms_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}
