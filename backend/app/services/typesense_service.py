"""Service — Integración con Typesense para búsqueda principal de productos."""

import asyncio
import logging
import re
import uuid
from datetime import UTC, datetime
from typing import Any, cast

import typesense
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from typesense.exceptions import ObjectAlreadyExists, ObjectNotFound

from app.core.config import settings
from app.models.location import Location
from app.models.product import Product

logger = logging.getLogger(__name__)

_client: typesense.Client | None = None



def _get_client() -> typesense.Client:
    global _client

    if _client is None:
        _client = typesense.Client(
            {
                "nodes": [
                    {
                        "host": settings.TYPESENSE_HOST,
                        "port": settings.TYPESENSE_PORT,
                        "protocol": settings.TYPESENSE_PROTOCOL,
                    }
                ],
                "api_key": settings.TYPESENSE_API_KEY,
                "connection_timeout_seconds": settings.TYPESENSE_TIMEOUT_SECONDS,
            }
        )
    return _client


def _sanitize_term(value: str) -> str:
    """Limpia entradas para evitar romper el filtro/query syntax de Typesense."""
    return re.sub(r"[^\w\-\s]", " ", value, flags=re.UNICODE).strip().lower()


def _infer_tags(product: Product) -> list[str]:
    """Genera tags livianos para mejorar facetado local."""
    raw = " ".join(
        [
            product.name or "",
            product.description or "",
            product.category or "",
        ]
    ).lower()
    tokens = re.findall(r"[\wáéíóúñ]{4,}", raw, flags=re.UNICODE)

    tags: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token in seen:
            continue
        seen.add(token)
        tags.append(token)
        if len(tags) >= 20:
            break
    return tags


async def ensure_products_collection() -> None:
    """Crea la colección de productos si no existe."""
    if not settings.TYPESENSE_API_KEY:
        logger.warning(
            "Typesense API key no configurada; se omite inicialización de colección"
        )
        return

    client = _get_client()
    collection_name = settings.TYPESENSE_COLLECTION_PRODUCTS

    schema: dict[str, Any] = {
        "name": collection_name,
        "fields": [
            {"name": "id", "type": "string"},
            {"name": "seller_id", "type": "string", "facet": True},
            {"name": "name", "type": "string"},
            {"name": "description", "type": "string", "optional": True},
            {"name": "category", "type": "string", "facet": True, "optional": True},
            {"name": "subcategory", "type": "string", "facet": True, "optional": True},
            {"name": "condition", "type": "string", "facet": True, "optional": True},
            {"name": "brand", "type": "string", "facet": True, "optional": True},
            {"name": "has_free_shipping", "type": "bool", "facet": True, "optional": True},
            {"name": "image_urls", "type": "string[]", "optional": True},
            {"name": "tags", "type": "string[]", "facet": True, "optional": True},
            {"name": "price", "type": "float", "facet": True},
            {"name": "is_active", "type": "bool", "facet": True},
            {"name": "is_deleted", "type": "bool", "facet": True},
            {"name": "location", "type": "geopoint", "optional": True},
            {"name": "seller_location_label", "type": "string", "optional": True},
            {"name": "created_at", "type": "int64"},
            {"name": "updated_at", "type": "int64"},
            {"name": "stock", "type": "int32", "facet": True, "optional": True},
            {"name": "discount_percentage", "type": "float", "facet": True, "optional": True},
            {"name": "warranty_days", "type": "int32", "facet": True, "optional": True},
            {"name": "is_returnable", "type": "bool", "facet": True, "optional": True},
            {"name": "fulfillment_type", "type": "string", "facet": True, "optional": True},
            {"name": "payment_methods", "type": "string[]", "facet": True, "optional": True},
            {"name": "promotions", "type": "string[]", "facet": True, "optional": True},
            {"name": "seller_rating", "type": "float", "facet": True, "optional": True},
        ],
        "default_sorting_field": "updated_at",
    }

    try:
        await asyncio.to_thread(client.collections.create, cast(Any, schema))
        logger.info("Colección Typesense '%s' creada", collection_name)
    except ObjectAlreadyExists:
        logger.debug("Colección Typesense '%s' ya existe", collection_name)


async def _get_seller_info(
    db: AsyncSession, seller_id: uuid.UUID
) -> tuple[float | None, float | None, str | None, float]:
    from app.models.user import User
    stmt = (
        select(
            func.ST_Y(Location.coordinates).label("lat"),
            func.ST_X(Location.coordinates).label("lng"),
            Location.label,
            User.average_rating,
        )
        .select_from(User)
        .outerjoin(Location, Location.user_id == User.id)
        .where(User.id == seller_id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None, None, None, 0.0

    lat = float(row.lat) if row.lat is not None else None
    lng = float(row.lng) if row.lng is not None else None
    label = row.label if isinstance(row.label, str) else None
    rating = float(row.average_rating) if row.average_rating is not None else 0.0
    return lat, lng, label, rating


def _to_epoch(value: datetime | None) -> int:
    if value is None:
        return int(datetime.now(UTC).timestamp())
    return int(value.timestamp())


async def build_product_document(db: AsyncSession, product: Product) -> dict[str, Any]:
    """Construye documento de índice con producto + ubicación de vendedor."""
    lat, lng, location_label, seller_rating = await _get_seller_info(
        db, product.seller_id
    )

    document: dict[str, Any] = {
        "id": str(product.id),
        "seller_id": str(product.seller_id),
        "name": product.name,
        "description": product.description or "",
        "category": (product.category or "").lower(),
        "subcategory": (product.subcategory or "").lower(),
        "condition": (product.condition or "nuevo").lower(),
        "brand": (product.brand or "").lower(),
        "has_free_shipping": bool(product.has_free_shipping),
        "image_urls": list(product.image_urls or []),
        "tags": _infer_tags(product),
        "price": float(product.price),
        "is_active": bool(product.is_active),
        "is_deleted": bool(product.is_deleted),
        "created_at": _to_epoch(product.created_at),
        "updated_at": _to_epoch(product.updated_at),
        "stock": product.stock if product.stock is not None else 1,
        "discount_percentage": (
            float(product.discount_percentage)
            if product.discount_percentage
            else 0.0
        ),
        "warranty_days": (
            product.warranty_days if product.warranty_days is not None else 0
        ),
        "is_returnable": (
            bool(product.is_returnable)
            if product.is_returnable is not None
            else False
        ),
        "fulfillment_type": product.fulfillment_type or "merchant",
        "payment_methods": list(product.payment_methods or []),
        "promotions": list(product.promotions or []),
        "seller_rating": seller_rating,
    }

    if lat is not None and lng is not None:
        document["location"] = [lat, lng]
    if location_label:
        document["seller_location_label"] = location_label

    return document


async def upsert_product_document(db: AsyncSession, product: Product) -> None:
    """Inserta o actualiza un documento de producto en Typesense."""
    if not settings.TYPESENSE_API_KEY:
        return

    await ensure_products_collection()
    client = _get_client()
    document = await build_product_document(db, product)

    await asyncio.to_thread(
        client.collections[settings.TYPESENSE_COLLECTION_PRODUCTS].documents.upsert,
        document,
    )


async def delete_product_document(product_id: uuid.UUID) -> None:
    """Elimina un documento del índice de Typesense si existe."""
    if not settings.TYPESENSE_API_KEY:
        return

    client = _get_client()
    try:
        await asyncio.to_thread(
            client.collections[settings.TYPESENSE_COLLECTION_PRODUCTS]
            .documents[str(product_id)]
            .delete
        )
    except ObjectNotFound:
        logger.debug("Documento %s no existe en Typesense; delete ignorado", product_id)


async def search_products(
    *,
    query_text: str,
    category: str | None = None,
    subcategory: str | None = None,
    brand: str | None = None,
    condition: str | None = None,
    has_free_shipping: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    availability: str | None = None,
    seller_rating_min: float | None = None,
    seller_rating_max: float | None = None,
    discount_only: bool | None = None,
    warranty: str | None = None,
    payment_methods: list[str] | None = None,
    tags: list[str] | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_meters: int | None = None,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    """Busca productos activos/no eliminados con filtros facetados y geo."""
    await ensure_products_collection()
    client = _get_client()

    q = query_text.strip() if query_text.strip() else "*"
    clean_tags = [_sanitize_term(tag) for tag in (tags or []) if _sanitize_term(tag)]
    if clean_tags:
        q = f"{q} {' '.join(clean_tags)}".strip()

    filters = ["is_active:=true", "is_deleted:=false"]

    if category:
        filters.append(f"category:={_sanitize_term(category)}")
    if subcategory:
        filters.append(f"subcategory:={_sanitize_term(subcategory)}")
    if brand:
        filters.append(f"brand:={_sanitize_term(brand)}")
    if condition:
        filters.append(f"condition:={_sanitize_term(condition)}")
    if has_free_shipping is True:
        filters.append("has_free_shipping:=true")

    if min_price is not None and max_price is not None:
        filters.append(f"price:[{min_price}..{max_price}]")
    elif min_price is not None:
        filters.append(f"price:>={min_price}")
    elif max_price is not None:
        filters.append(f"price:<={max_price}")

    if availability == "in_stock":
        filters.append("stock:>0")
    if discount_only is True:
        filters.append("discount_percentage:>0")
    if warranty == "has_warranty":
        filters.append("warranty_days:>0")

    if seller_rating_min is not None and seller_rating_max is not None:
        filters.append(f"seller_rating:[{seller_rating_min}..{seller_rating_max}]")
    elif seller_rating_min is not None:
        filters.append(f"seller_rating:>={seller_rating_min}")
    elif seller_rating_max is not None:
        filters.append(f"seller_rating:<={seller_rating_max}")

    if payment_methods:
        payment_methods_clean = [_sanitize_term(p) for p in payment_methods]
        pm_filter = ",".join(payment_methods_clean)
        filters.append(f"payment_methods:=[{pm_filter}]")

    if lat is not None and lng is not None and radius_meters and radius_meters > 0:
        radius_km = max(float(radius_meters) / 1000.0, 0.01)
        filters.append(f"location:({lat}, {lng}, {radius_km:.3f} km)")

    params: dict[str, Any] = {
        "q": q,
        "query_by": "name,description,category,subcategory,brand,tags",
        "per_page": max(1, min(limit, 100)),
        "num_typos": 2,
        "prefix": "true,true,true,true,true,true",
        "sort_by": "_text_match:desc,updated_at:desc",
        "facet_by": "category,subcategory,brand,condition,has_free_shipping",
    }

    if filters:
        params["filter_by"] = " && ".join(filters)

    result = await asyncio.to_thread(
        client.collections[settings.TYPESENSE_COLLECTION_PRODUCTS].documents.search,
        cast(Any, params),
    )

    hits = result.get("hits", [])
    documents: list[dict[str, Any]] = []
    for hit in hits:
        document = dict(hit.get("document", {}))

        geo_dist = hit.get("geo_distance_meters")
        if isinstance(geo_dist, dict):
            distance = geo_dist.get("location")
            if distance is not None:
                document["distance_meters"] = float(distance)

        documents.append(document)

    found = int(result.get("found", len(documents)))
    return documents, found
