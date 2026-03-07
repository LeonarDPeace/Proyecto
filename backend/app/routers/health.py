"""Router — Health Check.

Endpoint raíz para verificar que el servicio está activo.
Utilizado por Render, GitHub Actions y monitores de uptime.
"""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Verifica el estado del servicio.

    Returns:
        Estado, versión y entorno actual.
    """
    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
    )
