"""Esquemas Pydantic — Product.

Precios en COP. Imágenes como lista de URLs (máx. 5).
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.user import SellerPublicInfo


class ProductBase(BaseModel):
    """Campos comunes de producto."""

    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: float = Field(..., gt=0, description="Precio en COP (debe ser > 0)")
    category: str | None = Field(default=None, max_length=50)
    subcategory: str | None = Field(default=None, max_length=100)
    condition: str = Field(default="nuevo", max_length=50)
    brand: str | None = Field(default=None, max_length=100)
    has_free_shipping: bool = False
    stock: int = Field(default=1, ge=0)
    discount_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    warranty_days: int = Field(default=0, ge=0)
    is_returnable: bool = False
    fulfillment_type: str = Field(default="merchant", max_length=50)
    payment_methods: list[str] = Field(default_factory=lambda: ["efectivo", "transferencia"])
    promotions: list[str] = Field(default_factory=list)
    attributes: dict = Field(default_factory=dict)
    image_urls: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("image_urls")
    @classmethod
    def max_five_images(cls, v: list[str]) -> list[str]:
        """Máximo 5 imágenes por producto."""
        if len(v) > 5:
            msg = "Se permiten máximo 5 imágenes por producto"
            raise ValueError(msg)
        return v


class ProductCreate(ProductBase):
    """Datos requeridos para crear un producto."""

    pass


class ProductUpdate(BaseModel):
    """Datos opcionales para actualizar un producto."""

    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    category: str | None = None
    subcategory: str | None = None
    condition: str | None = None
    brand: str | None = None
    has_free_shipping: bool | None = None
    stock: int | None = Field(default=None, ge=0)
    discount_percentage: float | None = Field(default=None, ge=0.0, le=100.0)
    warranty_days: int | None = Field(default=None, ge=0)
    is_returnable: bool | None = None
    fulfillment_type: str | None = None
    payment_methods: list[str] | None = None
    promotions: list[str] | None = None
    attributes: dict | None = None
    image_urls: list[str] | None = None
    is_active: bool | None = None


class ProductRead(ProductBase):
    """Producto con metadata de lectura."""

    id: uuid.UUID
    seller_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductDetail(ProductRead):
    """Detalle de producto con vendedor público."""

    seller: SellerPublicInfo | None = None


class ProductSearchItem(BaseModel):
    """Resultado de búsqueda con metadatos de geolocalización opcionales."""

    id: uuid.UUID
    seller_id: uuid.UUID
    name: str
    description: str | None = None
    price: float
    category: str | None = None
    subcategory: str | None = None
    condition: str | None = None
    brand: str | None = None
    has_free_shipping: bool = False
    stock: int = 1
    discount_percentage: float = 0.0
    warranty_days: int = 0
    is_returnable: bool = False
    fulfillment_type: str = "merchant"
    payment_methods: list[str] = Field(default_factory=list)
    promotions: list[str] = Field(default_factory=list)
    image_urls: list[str] = Field(default_factory=list)
    is_active: bool = True
    seller_lat: float | None = None
    seller_lng: float | None = None
    seller_location_label: str | None = None
    distance_meters: float | None = None


class ProductSearchMeta(BaseModel):
    """Metadata para explicar el modo de búsqueda aplicado."""

    search_mode: Literal["semantic", "fallback_fulltext", "fulltext"]
    reason: str | None = None
    quota_remaining: int | None = None
    quota_limit: int | None = None
    query_clean: str | None = None
    category_applied: str | None = None
    subcategory_applied: str | None = None
    condition_applied: str | None = None
    brand_applied: str | None = None
    has_free_shipping_applied: bool | None = None
    min_price_applied: float | None = None
    max_price_applied: float | None = None
    tags_applied: list[str] = Field(default_factory=list)


class ProductSearchFilters(BaseModel):
    """Filtros avanzados (UI + NLU)."""

    category: str | None = None
    subcategory: str | None = None
    condition: str | None = None
    brand: str | None = None
    has_free_shipping: bool | None = None
    min_price: float | None = None
    max_price: float | None = None
    tags: list[str] = Field(default_factory=list)
    attributes: dict[str, str | list[str]] = Field(default_factory=dict)
    seller_rating_min: float | None = None
    seller_rating_max: float | None = None
    availability: str | None = None
    discount_only: bool | None = None
    warranty: str | None = None
    return_policy: str | None = None
    shipping_speed: str | None = None
    payment_methods: list[str] = Field(default_factory=list)
    promotions: list[str] = Field(default_factory=list)


class ProductSearchRequest(BaseModel):
    """Solicitud avanzada de búsqueda (preparada para UI compleja)."""

    query: str = Field(..., min_length=1)
    filters: ProductSearchFilters = Field(default_factory=ProductSearchFilters)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    radius_meters: int = Field(default=500, ge=10, le=5000)
    limit: int = Field(default=20, ge=1, le=100)


class ProductSearchResponse(BaseModel):
    """Respuesta del endpoint de búsqueda híbrida."""

    items: list[ProductSearchItem]
    total: int
    meta: ProductSearchMeta
