"""Router — Products (CRUD del catálogo P2P).

HU 3.1: Crear producto.
HU 3.2: Actualizar / ver producto.
HU 3.3: Eliminar producto (soft-delete) y pausar.
"""

import logging
import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_optional
from app.models.location import Location
from app.models.product import Product
from app.models.user import User
from app.schemas.product import (
    ProductCreate,
    ProductDetail,
    ProductRead,
    ProductSearchFilters,
    ProductSearchItem,
    ProductSearchMeta,
    ProductSearchRequest,
    ProductSearchResponse,
    ProductUpdate,
)
from app.schemas.response import MessageResponse
from app.schemas.user import SellerPublicInfo
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
        subcategory=product.subcategory,
        condition=product.condition,
        brand=product.brand,
        has_free_shipping=bool(product.has_free_shipping),
        stock=int(product.stock),
        discount_percentage=float(product.discount_percentage),
        warranty_days=int(product.warranty_days),
        is_returnable=bool(product.is_returnable),
        fulfillment_type=product.fulfillment_type,
        payment_methods=list(product.payment_methods or []),
        promotions=list(product.promotions or []),
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
        subcategory=str(document.get("subcategory", "")).strip() or None,
        condition=str(document.get("condition", "")).strip() or None,
        brand=str(document.get("brand", "")).strip() or None,
        has_free_shipping=bool(document.get("has_free_shipping", False)),
        stock=int(document.get("stock", 1)),
        discount_percentage=float(document.get("discount_percentage", 0.0)),
        warranty_days=int(document.get("warranty_days", 0)),
        is_returnable=bool(document.get("is_returnable", False)),
        fulfillment_type=str(document.get("fulfillment_type", "merchant")),
        payment_methods=[str(p) for p in document.get("payment_methods", [])],
        promotions=[str(p) for p in document.get("promotions", [])],
        image_urls=image_urls,
        is_active=bool(document.get("is_active", True)),
        seller_lat=seller_lat,
        seller_lng=seller_lng,
        seller_location_label=str(document.get("seller_location_label", "")).strip()
        or None,
        distance_meters=distance,
    )


def _merge_tags(primary: list[str] | None, secondary: list[str] | None) -> list[str]:
    tags: list[str] = []
    seen: set[str] = set()
    for source in (primary or [], secondary or []):
        for value in source:
            if not isinstance(value, str):
                continue
            cleaned = value.strip().lower()
            if not cleaned or cleaned in seen:
                continue
            seen.add(cleaned)
            tags.append(cleaned)
    return tags


async def _build_seller_public_info(
    db: AsyncSession, seller_id: uuid.UUID
) -> SellerPublicInfo | None:
    stmt = (
        select(User, Location)
        .outerjoin(Location, Location.user_id == User.id)
        .where(User.id == seller_id)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        return None

    user: User = row[0]
    location: Location | None = row[1]

    return SellerPublicInfo(
        id=user.id,
        name=user.name,
        role=user.role,
        reputation=float(user.reputation),
        average_rating=float(user.average_rating),
        total_reviews=int(user.total_reviews),
        is_verified=bool(user.is_verified),
        member_since=user.created_at,
        last_active_at=user.updated_at,
        location_label=location.label if location else None,
        location_campus=location.campus if location else None,
        email=user.email if user.show_email else None,
        phone=user.phone if user.show_phone else None,
    )


async def _run_hybrid_search(
    *,
    query_text: str,
    category: str | None,
    subcategory: str | None,
    condition: str | None,
    brand: str | None,
    has_free_shipping: bool | None,
    min_price: float | None,
    max_price: float | None,
    tags: list[str],
    lat: float | None,
    lng: float | None,
    radius_meters: int | None,
    limit: int,
    use_semantic: bool,
    current_user: User | None,
    db: AsyncSession,
    ui_filters: ProductSearchFilters | None = None,
) -> ProductSearchResponse:
    query_clean = query_text.strip()
    effective_category = category
    effective_subcategory = subcategory
    effective_condition = condition
    effective_brand = brand
    effective_has_free_shipping = has_free_shipping
    effective_min_price = min_price
    effective_max_price = max_price
    effective_availability = None
    effective_seller_rating_min = None
    effective_seller_rating_max = None
    effective_discount_only = None
    effective_warranty = None
    effective_payment_methods = None

    merged_tags = list(tags)

    if ui_filters is not None:
        effective_category = ui_filters.category or effective_category
        effective_subcategory = ui_filters.subcategory or effective_subcategory
        effective_condition = ui_filters.condition or effective_condition
        effective_brand = ui_filters.brand or effective_brand
        effective_has_free_shipping = (
            ui_filters.has_free_shipping
            if ui_filters.has_free_shipping is not None
            else effective_has_free_shipping
        )
        effective_min_price = (
            ui_filters.min_price
            if ui_filters.min_price is not None
            else effective_min_price
        )
        effective_max_price = (
            ui_filters.max_price
            if ui_filters.max_price is not None
            else effective_max_price
        )
        effective_availability = ui_filters.availability
        effective_seller_rating_min = ui_filters.seller_rating_min
        effective_seller_rating_max = ui_filters.seller_rating_max
        effective_discount_only = ui_filters.discount_only
        effective_warranty = ui_filters.warranty
        effective_payment_methods = ui_filters.payment_methods

        merged_tags = _merge_tags(merged_tags, ui_filters.tags)

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
                        if ui_filters is None:
                            nlu = await nlu_service.parse_semantic_query(query_text)
                        else:
                            nlu = await nlu_service.parse_semantic_query_with_filters(
                                query_text, ui_filters
                            )
                        search_mode = "semantic"
                        query_clean = nlu.query_clean
                        merged_tags = _merge_tags(merged_tags, nlu.tags)
                        if effective_category is None:
                            effective_category = nlu.category
                        if effective_subcategory is None:
                            effective_subcategory = nlu.subcategory
                        if effective_condition is None:
                            effective_condition = nlu.condition
                        if effective_brand is None:
                            effective_brand = nlu.brand
                        if effective_has_free_shipping is None:
                            effective_has_free_shipping = nlu.has_free_shipping
                        if effective_min_price is None:
                            effective_min_price = nlu.min_price
                        if effective_max_price is None:
                            effective_max_price = nlu.max_price
                        if effective_availability is None:
                            effective_availability = nlu.availability
                        if effective_seller_rating_min is None:
                            effective_seller_rating_min = nlu.seller_rating_min
                        if effective_seller_rating_max is None:
                            effective_seller_rating_max = nlu.seller_rating_max
                        if effective_discount_only is None:
                            effective_discount_only = nlu.discount_only
                        if effective_warranty is None:
                            effective_warranty = nlu.warranty
                        if effective_payment_methods is None and nlu.payment_methods:
                            effective_payment_methods = nlu.payment_methods
                    except Exception:
                        logger.exception(
                            "Error interpretando consulta NLU; se usa fallback full-text"
                        )
                        search_mode = "fallback_fulltext"
                        reason = "nlu_failed"
                        quota_consumed = False
                        quota_remaining = quota_remaining_before_consume
                        quota_limit = quota_limit_before_consume
                        query_clean = query_text.strip()
                        merged_tags = merged_tags or []
                else:
                    search_mode = "fallback_fulltext"
                    reason = "quota_exceeded"
            else:
                search_mode = "fallback_fulltext"
                reason = "quota_exceeded"
        except Exception:
            logger.exception(
                "No fue posible evaluar cuota semantica; se usa fallback full-text"
            )
            search_mode = "fallback_fulltext"
            reason = "quota_unavailable"
            quota_remaining = None
            quota_limit = None
            query_clean = query_text.strip()
            merged_tags = merged_tags or []
    elif use_semantic and current_user is None:
        search_mode = "fallback_fulltext"
        reason = "unauthenticated"

    try:
        docs, total = await typesense_service.search_products(
            query_text=query_clean,
            category=effective_category,
            subcategory=effective_subcategory,
            brand=effective_brand,
            condition=effective_condition,
            has_free_shipping=effective_has_free_shipping,
            min_price=effective_min_price,
            max_price=effective_max_price,
            availability=effective_availability,
            seller_rating_min=effective_seller_rating_min,
            seller_rating_max=effective_seller_rating_max,
            discount_only=effective_discount_only,
            warranty=effective_warranty,
            payment_methods=effective_payment_methods,
            tags=merged_tags,
            lat=lat,
            lng=lng,
            radius_meters=radius_meters if lat is not None and lng is not None else None,
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
                subcategory_applied=effective_subcategory,
                condition_applied=effective_condition,
                brand_applied=effective_brand,
                has_free_shipping_applied=effective_has_free_shipping,
                min_price_applied=effective_min_price,
                max_price_applied=effective_max_price,
                tags_applied=merged_tags,
            ),
        )
    except Exception:
        logger.exception(
            "Typesense no disponible; fallback a busqueda textual PostgreSQL"
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
                subcategory_applied=effective_subcategory,
                condition_applied=effective_condition,
                brand_applied=effective_brand,
                has_free_shipping_applied=effective_has_free_shipping,
                min_price_applied=effective_min_price,
                max_price_applied=effective_max_price,
                tags_applied=merged_tags,
            ),
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
    min_price: float | None = Query(None, ge=0, description="Precio mínimo COP"),
    max_price: float | None = Query(None, ge=0, description="Precio máximo COP"),
    availability: str | None = Query(None, description="Filtro de disponibilidad (in_stock)"),
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
    # Construir filtros de UI para pasar precio y disponibilidad al motor
    ui_filters = None
    if min_price is not None or max_price is not None or availability:
        ui_filters = ProductSearchFilters(
            min_price=min_price,
            max_price=max_price,
            availability=availability,
        )
    return await _run_hybrid_search(
        query_text=q,
        category=category,
        subcategory=None,
        condition=None,
        brand=None,
        has_free_shipping=None,
        min_price=min_price,
        max_price=max_price,
        tags=[],
        lat=lat,
        lng=lng,
        radius_meters=radius_meters,
        limit=limit,
        use_semantic=use_semantic,
        current_user=current_user,
        db=db,
        ui_filters=ui_filters,
    )


@router.post("/search/intelligent", response_model=ProductSearchResponse)
async def search_products_intelligent(
    payload: ProductSearchRequest,
    current_user: User | None = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
) -> ProductSearchResponse:
    """Busqueda inteligente con filtros de UI + NLU."""
    filters = payload.filters
    return await _run_hybrid_search(
        query_text=payload.query,
        category=filters.category,
        subcategory=filters.subcategory,
        condition=filters.condition,
        brand=filters.brand,
        has_free_shipping=filters.has_free_shipping,
        min_price=filters.min_price,
        max_price=filters.max_price,
        tags=filters.tags,
        lat=payload.lat,
        lng=payload.lng,
        radius_meters=payload.radius_meters,
        limit=payload.limit,
        use_semantic=True,
        current_user=current_user,
        db=db,
        ui_filters=filters,
    )


@router.get("/mine", response_model=list[ProductRead])
async def list_my_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ProductRead]:
    """Lista TODOS los productos del vendedor autenticado (incluye inactivos)."""
    return await product_service.list_products_by_seller(db, current_user.id)


@router.get("/{product_id}", response_model=ProductDetail)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProductDetail:
    """Obtiene el detalle de un producto activo por ID."""
    product = await product_service.get_product_by_id(db, product_id)
    seller_public = await _build_seller_public_info(db, product.seller_id)
    read_model = ProductRead.model_validate(product, from_attributes=True)
    return ProductDetail(**read_model.model_dump(), seller=seller_public)


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
