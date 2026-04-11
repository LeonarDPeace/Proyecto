"""Esquemas Pydantic — Ubicación del vendedor."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LocationUpsert(BaseModel):
    """Payload para crear/actualizar ubicación del vendedor."""

    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    campus: str | None = Field(default="UAO", max_length=100)
    label: str | None = Field(default=None, max_length=200)


class LocationRead(BaseModel):
    """Ubicación en formato listo para frontend."""

    id: uuid.UUID
    user_id: uuid.UUID
    campus: str
    label: str | None = None
    lat: float
    lng: float
    updated_at: datetime | None = None


class LocationDeleteResponse(BaseModel):
    """Respuesta de eliminación de ubicación."""

    deleted: bool
    message: str
