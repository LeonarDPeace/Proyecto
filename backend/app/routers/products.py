"""Router — Products (CRUD del catálogo P2P).

HU 3.1: Crear producto.
HU 3.2: Actualizar / ver producto.
HU 3.3: Eliminar producto (soft-delete) y pausar.
"""

import logging
import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.product import Product
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductRead,
    ProductSearchItem,
    ProductSearchMeta,
    ProductSearchResponse,
    ProductUpdate,
)
from app.schemas.response import MessageResponse
from app.services import nlu_service, product_service, quota_service, typesense_service

logger = logging.getLogger(__name__)

router = APIRouter()


def _product_to_search_item(product: Product) -> ProductSearchItem:
    return ProductSearchItem(
        id=product.id,
        seller_id=product.seller_id,
        name=product.name,
        description=product.description,
        price=float(product.price),
        category=product.category,
        image_urls=list(product.image_urls or []),
        is_active=bool(product.is_active),
    )


def _document_to_search_item(document: dict) -> ProductSearchItem:
    location = document.get("location")
    seller_lat: float | None = None
    seller_lng: float | None = None
    if isinstance(location, list) and len(location) == 2:
        try:
            seller_lat = float(location[0])
            seller_lng = float(location[1])
        except (TypeError, ValueError):
            seller_lat = None
            seller_lng = None

    image_urls_raw = document.get("image_urls")
    image_urls = [value for value in (image_urls_raw or []) if isinstance(value, str)]

    distance_raw = document.get("distance_meters")
    distance = float(distance_raw) if isinstance(distance_raw, int | float) else None

    return ProductSearchItem(
        id=uuid.UUID(str(document["id"])),
        seller_id=uuid.UUID(str(document["seller_id"])),
        name=str(document.get("name", "")),
        description=str(document.get("description", "")).strip() or None,
        price=float(document.get("price", 0)),
        category=str(document.get("category", "")).strip() or None,
        image_urls=image_urls,
        is_active=bool(document.get("is_active", True)),
        seller_lat=seller_lat,
        seller_lng=seller_lng,
        seller_location_label=str(document.get("seller_location_label", "")).strip()
        or None,
        distance_meters=distance,
    )


@router.get("/", response_model=list[ProductRead])
async def list_products(
    category: str | None = Query(None, description="Filtrar por categoría"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ProductRead]:
    """Lista productos activos del catálogo (Paginación y Filtros)."""
    return await product_service.list_products(
        db, category=category, limit=limit, offset=offset
    )


@router.get("/search", response_model=ProductSearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Texto libre de búsqueda"),
    category: str | None = Query(None, description="Filtro opcional por categoría"),
    lat: float | None = Query(None, ge=-90, le=90),
    lng: float | None = Query(None, ge=-180, le=180),
    radius_meters: int = Query(500, ge=10, le=5000),
    limit: int = Query(20, ge=1, le=100),
    use_semantic: bool = Query(
        True, description="Si es true, intenta NLU con cuota diaria"
    ),
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> ProductSearchResponse:
    """Búsqueda híbrida: Gemini (si hay cuota) + Typesense como motor principal."""
    query_clean = q.strip()
    tags: list[str] = []
    effective_category = category
    search_mode = "fulltext"
    reason: str | None = None
    quota_remaining: int | None = None
    quota_limit: int | None = None
    quota_consumed = False
    quota_remaining_before_consume: int | None = None
    quota_limit_before_consume: int | None = None

    if use_semantic and current_user is not None:
        try:
            snapshot = await quota_service.get_quota_snapshot(db, current_user.id)
            quota_remaining = snapshot.remaining
            quota_limit = snapshot.daily_limit
            quota_remaining_before_consume = snapshot.remaining
            quota_limit_before_consume = snapshot.daily_limit

            if snapshot.remaining > 0:
                (
                    quota_consumed,
                    snapshot_after,
                ) = await quota_service.try_consume_semantic_search(db, current_user.id)
                quota_remaining = snapshot_after.remaining
                quota_limit = snapshot_after.daily_limit

                if quota_consumed:
                    try:
                        nlu = await nlu_service.parse_semantic_query(q)
                        search_mode = "semantic"
                        query_clean = nlu.query_clean
                        tags = nlu.tags
                        if effective_category is None:
                            effective_category = nlu.category
                    except Exception:
                        logger.exception(
                            "Error interpretando consulta NLU; se usa fallback full-text"
                        )
                        search_mode = "fallback_fulltext"
                        reason = "nlu_failed"
                        quota_consumed = False
                        quota_remaining = quota_remaining_before_consume
                        quota_limit = quota_limit_before_consume
                        query_clean = q.strip()
                        tags = []
                else:
                    search_mode = "fallback_fulltext"
                    reason = "quota_exceeded"
            else:
                search_mode = "fallback_fulltext"
                reason = "quota_exceeded"
        except Exception:
            logger.exception(
                "No fue posible evaluar cuota semántica; se usa fallback full-text"
            )
            search_mode = "fallback_fulltext"
            reason = "quota_unavailable"
            quota_remaining = None
            quota_limit = None
            query_clean = q.strip()
            tags = []
    elif use_semantic and current_user is None:
        search_mode = "fallback_fulltext"
        reason = "unauthenticated"

    try:
        docs, total = await typesense_service.search_products(
            query_text=query_clean,
            category=effective_category,
            tags=tags,
            lat=lat,
            lng=lng,
            radius_meters=radius_meters
            if lat is not None and lng is not None
            else None,
            limit=limit,
        )

        items = [_document_to_search_item(document) for document in docs]

        if quota_consumed and search_mode == "semantic":
            await db.commit()

        return ProductSearchResponse(
            items=items,
            total=total,
            meta=ProductSearchMeta(
                search_mode=search_mode,
                reason=reason,
                quota_remaining=quota_remaining,
                quota_limit=quota_limit,
                query_clean=query_clean,
                category_applied=effective_category,
                tags_applied=tags,
            ),
        )
    except Exception:
        logger.exception(
            "Typesense no disponible; fallback a búsqueda textual PostgreSQL"
        )

        if quota_consumed:
            quota_consumed = False
            quota_remaining = quota_remaining_before_consume
            quota_limit = quota_limit_before_consume

        fallback_items = await product_service.search_products_text(
            db,
            query_clean,
            category=effective_category,
            limit=limit,
        )

        return ProductSearchResponse(
            items=[_product_to_search_item(product) for product in fallback_items],
            total=len(fallback_items),
            meta=ProductSearchMeta(
                search_mode="fallback_fulltext",
                reason=reason or "typesense_unavailable",
                quota_remaining=quota_remaining,
                quota_limit=quota_limit,
                query_clean=query_clean,
                category_applied=effective_category,
                tags_applied=tags,
            ),
        )


@router.get("/mine", response_model=list[ProductRead])
async def list_my_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ProductRead]:
    """Lista TODOS los productos del vendedor autenticado (incluye inactivos)."""
    return await product_service.list_products_by_seller(db, current_user.id)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    """Obtiene el detalle de un producto activo por ID."""
    return await product_service.get_product_by_id(db, product_id)


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    """Crea un nuevo producto en el catálogo (solo para Vendedores)."""
    if current_user.role != "vendedor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden crear productos",
        )

    product = await product_service.create_product(db, current_user.id, product_data)
    await db.commit()
    await db.refresh(product)

    try:
        await typesense_service.upsert_product_document(db, product)
    except Exception:
        logger.exception("No fue posible indexar producto creado en Typesense")

    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: uuid.UUID,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    """Actualiza un producto existente (solo el dueño)."""
    product = await product_service.update_product(
        db, product_id, current_user.id, product_data
    )
    await db.commit()
    await db.refresh(product)

    try:
        await typesense_service.upsert_product_document(db, product)
    except Exception:
        logger.exception("No fue posible indexar producto actualizado en Typesense")

    return product


@router.delete(
    "/{product_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_product(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Elimina (soft-delete) un producto."""
    await product_service.soft_delete_product(db, product_id, current_user.id)
    await db.commit()

    try:
        await typesense_service.delete_product_document(product_id)
    except Exception:
        logger.exception("No fue posible eliminar producto del índice Typesense")

    return MessageResponse(message="Producto eliminado exitosamente")


@router.patch(
    "/{product_id}/status",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
)
async def toggle_product_status(
    product_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProductRead:
    """Alterna el estado del producto (Pausar/Activar)."""
    product = await product_service.toggle_product_status(
        db, product_id, current_user.id
    )
    await db.commit()
    await db.refresh(product)

    try:
        await typesense_service.upsert_product_document(db, product)
    except Exception:
        logger.exception("No fue posible sincronizar estado de producto en Typesense")

    return product
