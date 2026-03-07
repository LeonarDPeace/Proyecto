"""Esquemas Pydantic — Product.

Precios en COP. Imágenes como lista de URLs (máx. 5).
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProductBase(BaseModel):
    """Campos comunes de producto."""

    name: str = Field(..., min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    price: float = Field(..., gt=0, description="Precio en COP (debe ser > 0)")
    category: str | None = Field(default=None, max_length=50)
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
