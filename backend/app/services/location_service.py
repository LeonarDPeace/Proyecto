"""Service — Gestión de ubicación del vendedor (perfil)."""

import uuid
from typing import Any

from geoalchemy2.elements import WKTElement
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location


async def get_user_location_view(
    db: AsyncSession, user_id: uuid.UUID
) -> dict[str, Any] | None:
    """Retorna ubicación de un usuario con coordenadas lat/lng parseadas."""
    stmt = (
        select(
            Location,
            func.ST_Y(Location.coordinates).label("lat"),
            func.ST_X(Location.coordinates).label("lng"),
        )
        .where(Location.user_id == user_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        return None

    location = row.Location
    lat = float(row.lat) if row.lat is not None else None
    lng = float(row.lng) if row.lng is not None else None

    return {
        "id": location.id,
        "user_id": location.user_id,
        "campus": location.campus,
        "label": location.label,
        "lat": lat,
        "lng": lng,
        "updated_at": location.updated_at,
    }


async def upsert_user_location(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    lat: float,
    lng: float,
    campus: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    """Crea o actualiza la ubicación de un usuario."""
    result = await db.execute(select(Location).where(Location.user_id == user_id))
    location = result.scalar_one_or_none()

    if location is None:
        location = Location(
            user_id=user_id,
            campus=(campus or "UAO").strip(),
            coordinates=WKTElement(f"POINT({lng} {lat})", srid=4326),
            label=label,
        )
        db.add(location)
    else:
        if campus is not None:
            location.campus = campus.strip() or location.campus
        location.coordinates = WKTElement(f"POINT({lng} {lat})", srid=4326)
        location.label = label

    await db.flush()

    saved = await get_user_location_view(db, user_id)
    if saved is None:
        raise RuntimeError("No se pudo leer la ubicación guardada")
    return saved


async def delete_user_location(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Elimina la ubicación del usuario. Retorna True si existía."""
    result = await db.execute(select(Location).where(Location.user_id == user_id))
    location = result.scalar_one_or_none()
    if location is None:
        return False

    await db.delete(location)
    await db.flush()
    return True
