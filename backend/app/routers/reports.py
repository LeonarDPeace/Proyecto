"""Router — Reports (Reportes de comportamiento indebido).

Sprint 5 — EP-07: Moderación y Reputación Comunitaria.
HU 7.3: Sistema de reporte por comportamiento indebido.

Endpoints:
- POST   /                         → Crear reporte (usuario autenticado)
- GET    /product/{product_id}     → Resumen de reportes de un producto
- GET    /admin/pending            → Lista reportes pendientes (admin)
- PATCH  /admin/{report_id}        → Revisar/desestimar reporte (admin)
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.report import ReportCreate, ReportRead, ReportSummary
from app.services import report_service

router = APIRouter()


@router.post(
    "/",
    response_model=ReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_report(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportRead:
    """Reporta un producto por comportamiento indebido.

    Razones disponibles: spam, offensive, fraud.
    Si el producto acumula 3 o más reportes, se oculta automáticamente.
    """
    report = await report_service.create_report(
        db,
        reporter_id=current_user.id,
        reason=data.reason,
        product_id=data.product_id,
        reported_user_id=data.reported_user_id,
        description=data.description,
    )
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/product/{product_id}", response_model=ReportSummary)
async def get_product_report_summary(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportSummary:
    """Obtiene el resumen de reportes de un producto."""
    return await report_service.get_product_report_summary(db, product_id)


@router.get("/admin/pending", response_model=list[ReportRead])
async def list_pending_reports(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ReportRead]:
    """Lista todos los reportes pendientes de revisión (solo administradores)."""
    if current_user.role != "admin":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta función",
        )
    return await report_service.list_pending_reports(db)


@router.patch("/admin/{report_id}", response_model=ReportRead)
async def review_report(
    report_id: uuid.UUID,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ReportRead:
    """Marca un reporte como revisado o desestimado (solo administradores)."""
    if current_user.role != "admin":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta función",
        )
    report = await report_service.review_report(db, report_id, new_status)
    await db.commit()
    await db.refresh(report)
    return report
