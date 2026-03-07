"""Router — Auth (Autenticación OTP — Sprint 1).

HU 1.1: Login con código OTP enviado al correo institucional.
HU 1.2: Creación de perfil (por defecto rol Comprador).
Flujo: request OTP → verify OTP → (si nuevo usuario) complete profile → JWT.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import (
    OTPRequest,
    OTPSentResponse,
    OTPVerify,
    ProfileCreate,
    ProfileUpdate,
    TokenResponse,
)
from app.schemas.user import UserPrivate
from app.services.auth_service import (
    create_user,
    generate_tokens,
    get_user_by_email,
    update_user_profile,
)
from app.services.email_service import create_otp, send_otp_email, verify_otp

router = APIRouter()


@router.post(
    "/otp/request",
    response_model=OTPSentResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar código OTP",
)
async def request_otp(
    payload: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Envía un código OTP de 6 dígitos al correo institucional.

    El código expira según OTP_EXPIRATION_MINUTES (por defecto 10 min).
    Funciona tanto para usuarios existentes como nuevos.
    """
    otp = await create_otp(db, payload.email)
    await send_otp_email(payload.email, otp.code)

    return OTPSentResponse(
        email=payload.email,
        expires_in_minutes=settings.OTP_EXPIRATION_MINUTES,
    )


@router.post(
    "/otp/verify",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar código OTP",
)
async def verify_otp_code(
    payload: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    """Verifica el código OTP y retorna un token JWT.

    Si el usuario ya existe, retorna el token directamente.
    Si es un usuario nuevo, retorna el token con is_new_user=True
    para que el frontend redirija a completar perfil.
    """
    is_valid = await verify_otp(db, payload.email, payload.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código OTP inválido, expirado o máximo de intentos alcanzado",
        )

    # Buscar si el usuario ya existe
    user = await get_user_by_email(db, payload.email)
    is_new = user is None

    if is_new:
        # Crear usuario temporal con datos mínimos — perfil se completa después
        user = await create_user(
            db,
            email=payload.email,
            name=payload.email.split("@")[0],  # Nombre temporal
            institutional_id=f"temp-{payload.email.split('@')[0]}",
        )

    tokens = generate_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        is_new_user=is_new,
    )


@router.post(
    "/profile/complete",
    response_model=UserPrivate,
    status_code=status.HTTP_200_OK,
    summary="Completar perfil de usuario",
)
async def complete_profile(
    payload: ProfileCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Completa el perfil del usuario después del primer registro (HU 1.2).

    Solo se permite si el usuario es nuevo (institutional_id temporal).
    Por defecto asigna rol Comprador.
    """
    user = await update_user_profile(
        db,
        current_user,
        name=payload.name,
        phone=payload.phone,
    )
    user.institutional_id = payload.institutional_id
    await db.flush()

    return user


@router.put(
    "/profile",
    response_model=UserPrivate,
    status_code=status.HTTP_200_OK,
    summary="Actualizar perfil",
)
async def update_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza el perfil del usuario autenticado (HU 1.2)."""
    user = await update_user_profile(
        db,
        current_user,
        name=payload.name,
        phone=payload.phone,
    )
    return user
