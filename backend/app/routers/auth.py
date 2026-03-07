"""Router — Auth (Autenticación y registro).

Endpoints para registro con correo institucional (.edu.co) y login con JWT.
Sprint 0: Flujo básico email/password. OAuth 2.0 completo en Sprint 1.
"""

from fastapi import APIRouter, HTTPException, status

from app.schemas.response import MessageResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register():
    """Registra un nuevo usuario con correo institucional.

    TODO (Sprint 1): Implementar lógica completa con BD.
    """
    return MessageResponse(message="Endpoint de registro — pendiente Sprint 1")


@router.post("/login", response_model=MessageResponse)
async def login():
    """Autentica un usuario y devuelve un token JWT.

    TODO (Sprint 1): Implementar lógica completa con BD + JWT.
    """
    return MessageResponse(message="Endpoint de login — pendiente Sprint 1")


@router.post("/refresh", response_model=MessageResponse)
async def refresh_token():
    """Renueva un token JWT expirado usando un refresh token.

    TODO (Sprint 1): Implementar refresh token rotation.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh tokens — pendiente Sprint 1",
    )
