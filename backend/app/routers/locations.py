"""Router — Locations (setup de ubicación para vendedores)."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.location import LocationDeleteResponse, LocationRead, LocationUpsert
from app.services import location_service, product_service, typesense_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/me", response_model=LocationRead | None)
async def get_my_location(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationRead | None:
    """Obtiene la ubicación del usuario autenticado."""
    location = await location_service.get_user_location_view(db, current_user.id)
    if location is None:
        return None
    return LocationRead.model_validate(location)


@router.put("/me", response_model=LocationRead)
async def upsert_my_location(
    payload: LocationUpsert,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationRead:
    """Crea o actualiza la ubicación del vendedor en el campus."""
    if current_user.role != "vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden configurar ubicación",
        )

    saved = await location_service.upsert_user_location(
        db,
        current_user.id,
        lat=payload.lat,
        lng=payload.lng,
        campus=payload.campus,
        label=payload.label,
    )
    await db.commit()

    # Best-effort: refrescar ubicación en el índice de productos del vendedor.
    try:
        products = await product_service.list_products_by_seller(db, current_user.id)
        for product in products:
            await typesense_service.upsert_product_document(db, product)
    except Exception:
        logger.exception("No fue posible sincronizar ubicación en Typesense")

    return LocationRead.model_validate(saved)


@router.delete("/me", response_model=LocationDeleteResponse)
async def delete_my_location(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationDeleteResponse:
    """Elimina la ubicación del usuario autenticado."""
    deleted = await location_service.delete_user_location(db, current_user.id)
    await db.commit()

    if deleted:
        try:
            products = await product_service.list_products_by_seller(
                db, current_user.id
            )
            for product in products:
                await typesense_service.upsert_product_document(db, product)
        except Exception:
            logger.exception(
                "No fue posible limpiar ubicación de productos en Typesense"
            )

    return LocationDeleteResponse(
        deleted=deleted,
        message="Ubicación eliminada" if deleted else "No había ubicación registrada",
    )
