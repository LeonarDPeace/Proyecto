"""Service — Report (HU 7.3).

Lógica de reportes de comportamiento indebido y auto-moderación.
Si un producto acumula >= AUTO_HIDE_THRESHOLD reportes, se oculta
automáticamente (is_active=false) hasta revisión administrativa.
"""

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.report import AUTO_HIDE_THRESHOLD, Report

logger = logging.getLogger(__name__)


async def create_report(
    db: AsyncSession,
    reporter_id: uuid.UUID,
    reason: str,
    product_id: uuid.UUID | None = None,
    reported_user_id: uuid.UUID | None = None,
    description: str | None = None,
) -> Report:
    """Crea un reporte sobre un producto o usuario.

    Valida que:
    - Si es de producto, el producto exista.
    - El reportante no sea el denunciado (auto-reporte).
    - No haya reportes duplicados del mismo emisor al mismo objetivo.
    """
    final_reported_user_id = reported_user_id

    if product_id:
        # Obtener el producto
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.is_deleted == False,  # noqa: E712
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        final_reported_user_id = product.seller_id
    elif not final_reported_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar product_id o reported_user_id",
        )

    # No permitir auto-reporte
    if final_reported_user_id == reporter_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes reportarte a ti mismo",
        )

    # Verificar reporte duplicado
    query = select(Report).where(Report.reporter_id == reporter_id)
    if product_id:
        query = query.where(Report.product_id == product_id)
    else:
        query = query.where(
            Report.reported_user_id == final_reported_user_id,
            Report.product_id == None,  # noqa: E711
        )

    existing = await db.execute(query)
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya realizaste este reporte anteriormente",
        )

    report = Report(
        reporter_id=reporter_id,
        reported_user_id=final_reported_user_id,
        product_id=product_id,
        reason=reason,
        description=description,
    )
    db.add(report)
    await db.flush()

    # Verificar umbral de auto-ocultamiento (solo si hay producto)
    if product_id:
        await _check_auto_hide(db, product_id)

    return report


async def _check_auto_hide(db: AsyncSession, product_id: uuid.UUID) -> None:
    """Oculta automáticamente un producto si alcanza el umbral de reportes.

    HU 7.3: Si un producto recibe >= AUTO_HIDE_THRESHOLD reportes,
    el sistema lo oculta (is_active=false) hasta revisión administrativa.
    """
    result = await db.execute(
        select(func.count(Report.id)).where(
            Report.product_id == product_id,
            Report.status == "pending",
        )
    )
    count = result.scalar() or 0

    if count >= AUTO_HIDE_THRESHOLD:
        await db.execute(
            Product.__table__.update()
            .where(Product.id == product_id)
            .values(is_active=False)
        )
        await db.flush()
        logger.warning(
            "Producto %s auto-ocultado por alcanzar %d reportes (umbral=%d)",
            product_id,
            count,
            AUTO_HIDE_THRESHOLD,
        )


async def get_product_report_summary(db: AsyncSession, product_id: uuid.UUID) -> dict:
    """Obtiene el resumen de reportes de un producto."""
    # Contar total
    total_result = await db.execute(
        select(func.count(Report.id)).where(Report.product_id == product_id)
    )
    total = total_result.scalar() or 0

    # Contar por razón
    reason_result = await db.execute(
        select(Report.reason, func.count(Report.id))
        .where(Report.product_id == product_id)
        .group_by(Report.reason)
    )
    reports_by_reason = dict(reason_result.all())

    # Verificar si el producto fue auto-ocultado
    product_result = await db.execute(
        select(Product.is_active).where(Product.id == product_id)
    )
    product_row = product_result.one_or_none()
    is_auto_hidden = not product_row.is_active if product_row else False

    return {
        "product_id": product_id,
        "total_reports": total,
        "is_auto_hidden": is_auto_hidden,
        "reports_by_reason": reports_by_reason,
    }


async def list_reports_for_product(
    db: AsyncSession, product_id: uuid.UUID
) -> list[Report]:
    """Lista todos los reportes de un producto (para revisión administrativa)."""
    result = await db.execute(
        select(Report)
        .where(Report.product_id == product_id)
        .order_by(Report.created_at.desc())
    )
    return list(result.scalars().all())


async def list_pending_reports(db: AsyncSession) -> list[Report]:
    """Lista todos los reportes pendientes de revisión (admin)."""
    result = await db.execute(
        select(Report)
        .where(Report.status == "pending")
        .order_by(Report.created_at.asc())
    )
    return list(result.scalars().all())


async def review_report(
    db: AsyncSession,
    report_id: uuid.UUID,
    new_status: str,
) -> Report:
    """Actualiza el estado de un reporte (reviewed / dismissed).

    Si se desestima (dismissed) y el producto fue auto-ocultado,
    se puede reactivar manualmente después.
    """
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reporte no encontrado",
        )

    if new_status not in ("reviewed", "dismissed"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Estado inválido. Use 'reviewed' o 'dismissed'",
        )

    report.status = new_status
    await db.flush()
    return report
