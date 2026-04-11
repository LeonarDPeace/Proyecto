"""Service — Control de cuota diaria para búsquedas inteligentes."""

import uuid
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user_search_quota import UserSearchQuota


@dataclass(slots=True)
class QuotaSnapshot:
    """Estado de cuota diaria para un usuario."""

    business_date: date
    daily_limit: int
    searches_used: int
    remaining: int


def _business_date_iso() -> date:
    tz = ZoneInfo(settings.BUSINESS_TIMEZONE)
    return datetime.now(tz).date()


def _base_quota_query(user_id: uuid.UUID, business_date: date):
    return select(UserSearchQuota).where(
        UserSearchQuota.user_id == user_id,
        UserSearchQuota.search_date == business_date,
    )


async def get_quota_snapshot(db: AsyncSession, user_id: uuid.UUID) -> QuotaSnapshot:
    """Obtiene la cuota del día sin crear fila cuando no existe."""
    business_date = _business_date_iso()
    result = await db.execute(_base_quota_query(user_id, business_date))
    quota = result.scalar_one_or_none()

    daily_limit = quota.daily_limit if quota else settings.SEMANTIC_DAILY_LIMIT
    searches_used = quota.searches_used if quota else 0
    remaining = max(0, daily_limit - searches_used)

    return QuotaSnapshot(
        business_date=business_date,
        daily_limit=daily_limit,
        searches_used=searches_used,
        remaining=remaining,
    )


async def try_consume_semantic_search(
    db: AsyncSession, user_id: uuid.UUID
) -> tuple[bool, QuotaSnapshot]:
    """Consume 1 crédito de búsqueda inteligente si hay disponibilidad."""
    business_date = _business_date_iso()
    query = _base_quota_query(user_id, business_date).with_for_update()
    result = await db.execute(query)
    quota = result.scalar_one_or_none()

    if quota is None:
        quota = UserSearchQuota(
            user_id=user_id,
            search_date=business_date,
            searches_used=0,
            daily_limit=settings.SEMANTIC_DAILY_LIMIT,
        )
        db.add(quota)
        await db.flush()

    if quota.searches_used >= quota.daily_limit:
        snapshot = QuotaSnapshot(
            business_date=business_date,
            daily_limit=quota.daily_limit,
            searches_used=quota.searches_used,
            remaining=0,
        )
        return False, snapshot

    quota.searches_used += 1
    await db.flush()

    snapshot = QuotaSnapshot(
        business_date=business_date,
        daily_limit=quota.daily_limit,
        searches_used=quota.searches_used,
        remaining=max(0, quota.daily_limit - quota.searches_used),
    )
    return True, snapshot
