"""Esquemas Pydantic — Coupon (Sprint 5 — HU 8.9).

Sistema de cupones de descuento para vendedores.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class CouponCreate(BaseModel):
    """Datos para crear un cupón de descuento."""

    code: str = Field(
        ..., min_length=3, max_length=30, description="Código alfanumérico (ej. VERA20)"
    )
    discount_percent: float | None = Field(
        default=None, gt=0, le=100, description="Descuento porcentual (1-100)"
    )
    discount_fixed_cop: float | None = Field(
        default=None, gt=0, description="Descuento en valor fijo COP"
    )
    max_uses: int = Field(default=1, ge=1, description="Máximo de usos")
    expires_at: datetime | None = None
    applicable_product_ids: list[uuid.UUID] | None = Field(
        default=None, description="Lista de IDs de productos a los que aplica (opcional)"
    )

    @model_validator(mode="after")
    def exactly_one_discount_type(self) -> "CouponCreate":
        """Valida que se especifique exactamente un tipo de descuento."""
        has_percent = self.discount_percent is not None
        has_fixed = self.discount_fixed_cop is not None
        if has_percent == has_fixed:
            msg = "Debe especificar exactamente uno: discount_percent o discount_fixed_cop"
            raise ValueError(msg)
        return self


class CouponUpdate(BaseModel):
    """Datos opcionales para actualizar un cupón."""

    is_active: bool | None = None
    max_uses: int | None = Field(default=None, ge=1)
    expires_at: datetime | None = None


class CouponRead(BaseModel):
    """Datos de lectura de un cupón."""

    id: uuid.UUID
    seller_id: uuid.UUID
    code: str
    discount_percent: float | None
    discount_fixed_cop: float | None
    max_uses: int
    current_uses: int
    is_active: bool
    expires_at: datetime | None
    created_at: datetime
    applicable_product_ids: list[uuid.UUID] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def map_products_to_ids(cls, data: any) -> any:
        """Extrae los IDs de la relación de productos de forma segura."""
        # Si ya tiene los IDs, no hacer nada
        if isinstance(data, dict) and "applicable_product_ids" in data:
            return data
            
        # Intentar extraer de la relación 'applicable_products'
        prods = []
        if hasattr(data, "__dict__") and "applicable_products" in data.__dict__:
            prods = data.applicable_products
        elif isinstance(data, dict) and "applicable_products" in data:
            prods = data["applicable_products"]

        if prods:
            ids = [p.id if hasattr(p, "id") else (p["id"] if isinstance(p, dict) else p) for p in prods]
            if isinstance(data, dict):
                data["applicable_product_ids"] = ids
            else:
                # Si es un objeto de SQLAlchemy, no podemos mutarlo así, 
                # pero Pydantic lo manejará si devolvemos un dict
                obj_data = {c.name: getattr(data, c.name) for c in data.__table__.columns}
                obj_data["applicable_product_ids"] = ids
                return obj_data
        
        return data

    model_config = {"from_attributes": True}


class CouponValidation(BaseModel):
    """Resultado de validación de un cupón."""

    valid: bool
    code: str
    discount_amount: float = 0.0
    message: str
