"""Router — Analytics (Dashboard financiero).

Sprint 5 — EP-08: Gestión Avanzada de Pedidos.
HU 8.7: Dashboard Financiero con Rangos Temporales variables.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.analytics import AnalyticsDataPoint, AnalyticsSummary
from app.services import analytics_service

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_seller_summary(
    period: Literal["day", "week", "month", "semester", "all_time"] = Query(
        "month", description="Período de consulta"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsSummary:
    """Resumen financiero del vendedor para un período dado."""
    return await analytics_service.get_seller_summary(
        db, current_user.id, period=period
    )


@router.get("/timeline", response_model=list[AnalyticsDataPoint])
async def get_seller_timeline(
    period: Literal["day", "week", "month", "semester", "all_time"] = Query(
        "month", description="Período de consulta"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AnalyticsDataPoint]:
    """Puntos de datos diarios para gráficos del dashboard."""
    return await analytics_service.get_seller_timeline(
        db, current_user.id, period=period
    )
