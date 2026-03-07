"""Esquemas Pydantic — Respuestas estándar de la API."""

from pydantic import BaseModel


class MessageResponse(BaseModel):
    """Respuesta genérica con un mensaje."""

    message: str


class HealthResponse(BaseModel):
    """Respuesta del endpoint de health check."""

    status: str
    version: str
    environment: str
