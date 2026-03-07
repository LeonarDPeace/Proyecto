"""Service — Auth (HU 1.1, HU 1.2).

Lógica de autenticación OTP y gestión de perfiles de usuario.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.models.user import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Busca un usuario por email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    """Busca un usuario por ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    name: str,
    institutional_id: str,
    phone: str | None = None,
    role: str = "comprador",
) -> User:
    """Crea un nuevo usuario (HU 1.2 — por defecto rol Comprador).

    Args:
        db: Sesión de base de datos.
        email: Correo institucional (.edu.co).
        name: Nombre completo.
        institutional_id: Código institucional.
        phone: Teléfono (opcional).
        role: Rol por defecto "comprador".

    Returns:
        El usuario creado.
    """
    user = User(
        email=email.strip().lower(),
        name=name.strip(),
        institutional_id=institutional_id.strip(),
        phone=phone,
        role=role,
        accepted_terms_at=datetime.now(timezone.utc),
        is_verified=True,  # Verificado por OTP al email institucional
    )
    db.add(user)
    await db.flush()
    return user


def generate_tokens(user: User) -> dict:
    """Genera access token JWT para un usuario autenticado.

    Args:
        user: Usuario autenticado.

    Returns:
        Dict con access_token, token_type, y datos del usuario.
    """
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
    }


async def update_user_profile(
    db: AsyncSession,
    user: User,
    *,
    name: str | None = None,
    phone: str | None = None,
    show_email: bool | None = None,
    show_phone: bool | None = None,
) -> User:
    """Actualiza el perfil de un usuario (HU 1.2, HU 1.3).

    Args:
        db: Sesión de base de datos.
        user: Usuario a actualizar.
        name: Nuevo nombre (opcional).
        phone: Nuevo teléfono (opcional).
        show_email: Mostrar email en perfil público (opcional).
        show_phone: Mostrar teléfono en perfil público (opcional).

    Returns:
        El usuario actualizado.
    """
    if name is not None:
        user.name = name.strip()
    if phone is not None:
        user.phone = phone
    if show_email is not None:
        user.show_email = show_email
    if show_phone is not None:
        user.show_phone = show_phone

    user.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return user
