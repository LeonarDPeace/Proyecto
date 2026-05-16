"""Esquemas Pydantic — Auth (OTP flow, Sprint 1).

HU 1.1: Autenticación con código OTP.
HU 1.2: Creación de perfil de usuario.
HU 1.3: Configuración de privacidad.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator

# ---------------------------------------------------------------------------
# OTP — Request / Verify (HU 1.1)
# ---------------------------------------------------------------------------


class OTPRequest(BaseModel):
    """Solicitud de código OTP al correo institucional."""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def format_email(cls, v: str) -> str:
        """Formatea el correo a minúsculas."""
        return v.strip().lower()


class OTPVerify(BaseModel):
    """Verificación del código OTP + datos para primer registro."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

    @field_validator("email")
    @classmethod
    def format_email(cls, v: str) -> str:
        """Formatea el correo a minúsculas."""
        return v.strip().lower()


# ---------------------------------------------------------------------------
# Profile — Registro completo (HU 1.2)
# ---------------------------------------------------------------------------


class ProfileCreate(BaseModel):
    """Datos para completar el perfil de usuario (primer inicio de sesión)."""

    name: str = Field(..., min_length=2, max_length=150)
    institutional_id: str = Field(..., min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    accept_terms: bool = Field(
        ..., description="Aceptación explícita de T&C (Ley 1581/2012)"
    )

    @field_validator("accept_terms")
    @classmethod
    def must_accept_terms(cls, v: bool) -> bool:
        if not v:
            msg = "Debe aceptar los términos y condiciones (Ley 1581/2012)"
            raise ValueError(msg)
        return v


class ProfileUpdate(BaseModel):
    """Datos opcionales para actualizar el perfil."""

    name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=20)


# ---------------------------------------------------------------------------
# Privacy settings (HU 1.3)
# ---------------------------------------------------------------------------


class PrivacySettings(BaseModel):
    """Configuración de privacidad del usuario."""

    show_email: bool = Field(
        default=False,
        description="Mostrar email en perfil público",
    )
    show_phone: bool = Field(
        default=False,
        description="Mostrar teléfono en perfil público",
    )


class PrivacySettingsRead(PrivacySettings):
    """Lectura de configuración de privacidad (incluye valores actuales)."""

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Auth Responses
# ---------------------------------------------------------------------------


class TokenResponse(BaseModel):
    """Respuesta con token JWT tras autenticación exitosa."""

    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class OTPSentResponse(BaseModel):
    """Confirmación de envío de OTP."""

    message: str = "Código OTP enviado al correo"
    email: str
    expires_in_minutes: int
    is_registered: bool = False


class VendorRoleRequest(BaseModel):
    """Solicita rol de vendedor usando código Sinapsis."""

    sinapsis_code: str = Field(..., min_length=1, max_length=50)


class VendorRoleResponse(BaseModel):
    """Respuesta a solicitud de rol vendedor."""

    message: str
    vendor_status: str
    role: str
