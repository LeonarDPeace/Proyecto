"""Esquemas Pydantic — Rating (Sprint 5 — HU 7.1/7.2).

Calificación de transacciones (1 a 5 estrellas).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """Datos para crear una calificación tras transacción completada."""

    negotiation_id: uuid.UUID
    stars: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    comment: str | None = Field(
        default=None,
        max_length=500,
        description="Comentario opcional",
    )


class RatingRead(BaseModel):
    """Lectura de una calificación."""

    id: uuid.UUID
    negotiation_id: uuid.UUID
    reviewer_id: uuid.UUID
    reviewed_id: uuid.UUID
    stars: int
    comment: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserReputation(BaseModel):
    """Reputación consolidada de un usuario (HU 7.2)."""

    user_id: uuid.UUID
    average_rating: float
    total_reviews: int
