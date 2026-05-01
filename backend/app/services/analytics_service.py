"""Service — Analytics (HU 8.7).

Dashboard financiero con rangos temporales variables.
Consultas de agregación sobre la tabla transactions para el vendedor.
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

# Mapeo de períodos a timedelta
_PERIOD_DELTAS = {
    "day": timedelta(days=1),
    "week": timedelta(weeks=1),
    "month": timedelta(days=30),
    "semester": timedelta(days=180),
    "all_time": None,
}


async def get_seller_summary(
    db: AsyncSession,
    seller_id: uuid.UUID,
    period: str = "all_time",
) -> dict:
    """Calcula el resumen financiero de un vendedor para un período."""
    query = select(
        func.count(Transaction.id).label("total_transactions"),
        func.coalesce(func.sum(Transaction.total_cop), 0).label("total_revenue"),
        func.coalesce(func.sum(Transaction.discount_cop), 0).label("total_discount"),
        func.coalesce(func.avg(Transaction.total_cop), 0).label("avg_order"),
    ).where(Transaction.seller_id == seller_id)

    delta = _PERIOD_DELTAS.get(period)
    if delta is not None:
        since = datetime.now(UTC) - delta
        query = query.where(Transaction.completed_at >= since)

    result = await db.execute(query)
    row = result.one()

    total_rev = float(row.total_revenue)
    total_disc = float(row.total_discount)

    return {
        "seller_id": seller_id,
        "period": period,
        "total_transactions": row.total_transactions,
        "total_revenue_cop": total_rev,
        "total_discount_cop": total_disc,
        "net_revenue_cop": round(total_rev - total_disc, 2),
        "average_order_cop": round(float(row.avg_order), 2),
    }


async def get_seller_timeline(
    db: AsyncSession,
    seller_id: uuid.UUID,
    period: str = "month",
) -> list[dict]:
    """Genera puntos de datos diarios para gráficos del dashboard."""
    delta = _PERIOD_DELTAS.get(period, timedelta(days=30))
    if delta is None:
        delta = timedelta(days=365)

    since = datetime.now(UTC) - delta

    result = await db.execute(
        select(
            func.date_trunc("day", Transaction.completed_at).label("day"),
            func.sum(Transaction.total_cop).label("revenue"),
            func.count(Transaction.id).label("count"),
        )
        .where(
            Transaction.seller_id == seller_id,
            Transaction.completed_at >= since,
        )
        .group_by("day")
        .order_by("day")
    )

    return [
        {
            "date": str(row.day.date()) if row.day else "",
            "revenue_cop": float(row.revenue),
            "transaction_count": row.count,
        }
        for row in result.all()
    ]
