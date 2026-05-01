"""Router — Ratings (Calificaciones de transacciones).

Sprint 5 — EP-07: Moderación y Reputación Comunitaria.
HU 7.1: Calificación de transacciones (1 a 5 estrellas).
HU 7.2: Visualización de reputación en el perfil.
"""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingRead, UserReputation
from app.services import rating_service

router = APIRouter()


@router.post(
    "/",
    response_model=RatingRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_rating(
    data: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RatingRead:
    """Califica una transacción completada (1 a 5 estrellas)."""
    rating = await rating_service.create_rating(
        db,
        reviewer_id=current_user.id,
        negotiation_id=data.negotiation_id,
        stars=data.stars,
        comment=data.comment,
    )
    await db.commit()
    await db.refresh(rating)
    return rating


@router.get("/user/{user_id}/reputation", response_model=UserReputation)
async def get_user_reputation(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> UserReputation:
    """Obtiene la reputación consolidada de un usuario (HU 7.2)."""
    return await rating_service.get_user_reputation(db, user_id)


@router.get("/user/{user_id}", response_model=list[RatingRead])
async def list_user_ratings(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[RatingRead]:
    """Lista las calificaciones recibidas por un usuario."""
    return await rating_service.list_ratings_for_user(db, user_id)
