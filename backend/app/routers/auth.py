"""Router — Auth (Autenticación OTP — Sprint 1).

HU 1.1: Login con código OTP enviado al correo electrónico.
HU 1.2: Creación de perfil.
Flujo: request OTP → verify OTP → (si nuevo usuario) complete profile → JWT.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user, security_scheme
from app.models.user import User
from app.schemas.auth import (
    OTPRequest,
    OTPSentResponse,
    OTPVerify,
    ProfileCreate,
    ProfileUpdate,
    TokenResponse,
    VendorRoleRequest,
    VendorRoleResponse,
)
from app.schemas.user import UserPrivate
from app.services.auth_service import (
    create_user,
    generate_tokens,
    get_user_by_email,
    update_user_profile,
)
from app.services.email_service import create_otp, send_otp_email, verify_otp
from app.services.sinapsis_service import request_vendor_role

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
    """Envía un código OTP de 6 dígitos al correo electrónico."""
    user = await get_user_by_email(db, payload.email)
    is_registered = user is not None

    otp = await create_otp(db, payload.email)
    await send_otp_email(payload.email, otp.code)

    await db.commit()

    return OTPSentResponse(
        email=payload.email,
        expires_in_minutes=settings.OTP_EXPIRATION_MINUTES,
        is_registered=is_registered,
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
    """Verifica el código OTP y retorna un token JWT."""
    is_valid = await verify_otp(db, payload.email, payload.code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Código OTP inválido, expirado o máximo de intentos alcanzado",
        )

    user = await get_user_by_email(db, payload.email)
    is_new = user is None

    if is_new:
        from app.core.security import create_access_token
        # Create a pending token, DO NOT save user to DB yet.
        pending_token = create_access_token(data={"sub": "pending", "pending_email": payload.email, "role": "pending"})
        return TokenResponse(
            access_token=pending_token,
            token_type="bearer",
            is_new_user=True,
        )

    await db.commit()

    tokens = generate_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        is_new_user=False,
    )


@router.post(
    "/profile/complete",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Completar perfil de usuario",
)
async def complete_profile(
    payload: ProfileCreate,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Completa el perfil del usuario (creándolo en BD por primera vez) y devuelve token real."""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
        
    from app.core.security import decode_access_token
    token_data = decode_access_token(credentials.credentials)
    if not token_data or token_data.get("sub") != "pending" or not token_data.get("pending_email"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de registro inválido")
        
    email = token_data["pending_email"]
    
    user = await get_user_by_email(db, email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya está registrado")

    user = await create_user(
        db,
        email=email,
        name=payload.name,
        institutional_id=payload.institutional_id,
        phone=payload.phone,
    )
    
    await db.commit()

    tokens = generate_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        is_new_user=False,
    )


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
    await db.commit()
    return user


@router.post(
    "/vendor/request",
    response_model=VendorRoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Solicitar rol de vendedor con código Sinapsis (HU 1.4)",
)
async def vendor_role_request(
    request: VendorRoleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """HU 1.4 y 1.5: El usuario autenticado solicita el rol de vendedor.

    El sistema valida el código ingresado contra la whitelist (CSV) y
    actualiza su rol si es correcto.
    """
    vendor_status, new_role = await request_vendor_role(
        db=db, user=current_user, sinapsis_code=request.sinapsis_code
    )
    return VendorRoleResponse(
        message="Solicitud procesada correctamente.",
        vendor_status=vendor_status,
        role=new_role,
    )


@router.post(
    "/profile/switch-role",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar rol entre comprador y vendedor (HU 5.x)",
)
async def switch_role(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permite a un emprendedor aprobado alternar su interfaz/rol.
    Retorna un nuevo token JWT con el rol actualizado.
    """
    if current_user.vendor_status != "approved":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los emprendedores aprobados pueden alternar roles.",
        )

    from app.services.auth_service import switch_user_role

    user = await switch_user_role(db, current_user)
    await db.commit()
    await db.refresh(user)

    tokens = generate_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        token_type=tokens["token_type"],
        is_new_user=False,
    )

