"""Esquemas Pydantic — Report (HU 7.3).

Sprint 5 — EP-07: Moderación y Reputación Comunitaria.
HU 7.3: Sistema de reporte por comportamiento indebido.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ReportCreate(BaseModel):
    """Datos para crear un reporte de comportamiento indebido."""

    product_id: uuid.UUID | None = Field(default=None, description="ID del producto (si aplica)")
    reported_user_id: uuid.UUID | None = Field(default=None, description="ID del usuario (obligatorio si no hay product_id)")
    reason: Literal["spam", "offensive", "fraud"] = Field(
        description="Razón del reporte: spam, offensive (ofensivo), fraud (fraude)"
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Descripción adicional opcional del reporte",
    )


class ReportRead(BaseModel):
    """Datos de lectura de un reporte."""

    id: uuid.UUID
    reporter_id: uuid.UUID
    reported_user_id: uuid.UUID
    product_id: uuid.UUID | None
    reason: str
    description: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportSummary(BaseModel):
    """Resumen de reportes de un producto."""

    product_id: uuid.UUID
    total_reports: int
    is_auto_hidden: bool
    reports_by_reason: dict[str, int]
