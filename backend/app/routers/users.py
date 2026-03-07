"""Router — Users (perfil y búsqueda de usuarios).

Respeta la separación público/privado (Ley 1581/2012).
Sprint 0: Stubs con la estructura de endpoints.
"""

from fastapi import APIRouter

from app.schemas.response import MessageResponse
from app.schemas.user import UserPublic

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def get_current_user():
    """Obtiene el perfil del usuario autenticado.

    TODO (Sprint 1): Implementar con JWT dependency.
    """
    return MessageResponse(message="Pendiente Sprint 1")


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: str):
    """Obtiene el perfil público de un usuario.

    Nota: email y phone solo visibles con negociación aceptada (RLS).

    TODO (Sprint 1): Implementar con BD + RLS enforcement.
    """
    return MessageResponse(message="Pendiente Sprint 1")
