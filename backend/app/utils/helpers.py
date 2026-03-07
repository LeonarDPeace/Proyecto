"""Utilidades generales del backend."""

from datetime import datetime, timezone


def now_bogota() -> datetime:
    """Retorna la fecha/hora actual en UTC (para almacenar en BD).

    Nota: Se almacena en UTC y se presenta en America/Bogota en el frontend.
    """
    return datetime.now(timezone.utc)
