"""Service — Rating (HU 7.1 / 7.2).

Lógica de calificación de transacciones y cálculo de reputación.
"""

import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.negotiation import Negotiation
from app.models.rating import Rating
from app.models.user import User

logger = logging.getLogger(__name__)


async def create_rating(
    db: AsyncSession,
    reviewer_id: uuid.UUID,
    negotiation_id: uuid.UUID,
    stars: int,
    comment: str | None = None,
) -> Rating:
    """Crea una calificación para una negociación completada.

    Valida que:
    - La negociación exista y esté en estado 'delivered'.
    - El usuario sea parte de la negociación.
    - No haya calificado previamente la misma negociación.
    """
    result = await db.execute(
        select(Negotiation).where(Negotiation.id == negotiation_id)
    )
    negotiation = result.scalar_one_or_none()

    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negociación no encontrada",
        )

    if negotiation.status != "delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede calificar negociaciones completadas (delivered)",
        )

    if reviewer_id not in (negotiation.buyer_id, negotiation.seller_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    # Determinar a quién se califica
    reviewed_id = (
        negotiation.seller_id if reviewer_id == negotiation.buyer_id else negotiation.buyer_id
    )

    # Verificar duplicado
    existing = await db.execute(
        select(Rating).where(
            Rating.negotiation_id == negotiation_id,
            Rating.reviewer_id == reviewer_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya calificaste esta negociación",
        )

    rating = Rating(
        negotiation_id=negotiation_id,
        reviewer_id=reviewer_id,
        reviewed_id=reviewed_id,
        stars=stars,
        comment=comment,
    )
    db.add(rating)
    await db.flush()

    # Actualizar promedios del usuario calificado
    await _update_user_reputation(db, reviewed_id)

    return rating


async def _update_user_reputation(
    db: AsyncSession, user_id: uuid.UUID
) -> None:
    """Recalcula average_rating y total_reviews de un usuario."""
    result = await db.execute(
        select(
            func.count(Rating.id).label("total"),
            func.coalesce(func.avg(Rating.stars), 0).label("avg"),
        ).where(Rating.reviewed_id == user_id)
    )
    row = result.one()
    await db.execute(
        User.__table__.update()
        .where(User.id == user_id)
        .values(
            average_rating=round(float(row.avg), 2),
            total_reviews=int(row.total),
        )
    )
    await db.flush()
    logger.info("Reputación actualizada para user=%s: avg=%.2f, total=%d", user_id, row.avg, row.total)


async def get_user_reputation(
    db: AsyncSession, user_id: uuid.UUID
) -> dict:
    """Obtiene la reputación consolidada de un usuario."""
    result = await db.execute(
        select(User.average_rating, User.total_reviews).where(User.id == user_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    return {
        "user_id": user_id,
        "average_rating": float(row.average_rating),
        "total_reviews": row.total_reviews,
    }


async def list_ratings_for_user(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Rating]:
    """Lista las calificaciones recibidas por un usuario."""
    result = await db.execute(
        select(Rating)
        .where(Rating.reviewed_id == user_id)
        .order_by(Rating.created_at.desc())
    )
    return list(result.scalars().all())
