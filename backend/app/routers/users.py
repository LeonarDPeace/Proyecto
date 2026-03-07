"""Router — Users (perfil y privacidad — Sprint 1).

HU 1.2: Gestión de perfil de usuario.
HU 1.3: Configuración de privacidad.
Respeta la separación público/privado (Ley 1581/2012).
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.auth import PrivacySettings, PrivacySettingsRead
from app.schemas.user import UserPrivate, UserPublic
from app.services.auth_service import get_user_by_id, update_user_profile

router = APIRouter()


@router.get(
    "/me",
    response_model=UserPrivate,
    summary="Mi perfil (datos completos)",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Obtiene el perfil completo del usuario autenticado.

    Incluye email, phone, y datos sensibles (solo visible al propio usuario).
    """
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    summary="Perfil público de un usuario",
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Obtiene el perfil público de un usuario.

    Solo muestra nombre, rol y reputación.
    Email y phone solo visibles si el usuario lo permite en su configuración
    de privacidad (HU 1.3) o hay negociación aceptada.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return user


# ---------------------------------------------------------------------------
# Privacy settings (HU 1.3)
# ---------------------------------------------------------------------------


@router.get(
    "/me/privacy",
    response_model=PrivacySettingsRead,
    summary="Obtener config de privacidad",
)
async def get_privacy_settings(current_user: User = Depends(get_current_user)):
    """Obtiene la configuración de privacidad del usuario autenticado."""
    return PrivacySettingsRead(
        show_email=current_user.show_email,
        show_phone=current_user.show_phone,
    )


@router.put(
    "/me/privacy",
    response_model=PrivacySettingsRead,
    summary="Actualizar config de privacidad",
)
async def update_privacy_settings(
    payload: PrivacySettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualiza la configuración de privacidad (HU 1.3).

    Permite al usuario decidir si mostrar u ocultar su email y teléfono
    en su perfil público. Por defecto, ambos están ocultos.
    """
    user = await update_user_profile(
        db,
        current_user,
        show_email=payload.show_email,
        show_phone=payload.show_phone,
    )
    return PrivacySettingsRead(
        show_email=user.show_email,
        show_phone=user.show_phone,
    )
