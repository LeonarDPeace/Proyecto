"""Service — Coupon (HU 8.9).

CRUD y validación de cupones de descuento para vendedores.
"""

import logging
import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.coupon import Coupon
from app.models.product import Product
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_coupon(
    db: AsyncSession,
    seller_id: uuid.UUID,
    code: str,
    discount_percent: float | None = None,
    discount_fixed_cop: float | None = None,
    max_uses: int = 1,
    expires_at=None,
    applicable_product_ids: list[uuid.UUID] | None = None,
) -> Coupon:
    """Crea un nuevo cupón de descuento."""
    # Verificar código único
    existing = await db.execute(select(Coupon).where(Coupon.code == code.upper()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un cupón con el código '{code}'",
        )

    coupon = Coupon(
        seller_id=seller_id,
        code=code.upper(),
        discount_percent=discount_percent,
        discount_fixed_cop=discount_fixed_cop,
        max_uses=max_uses,
        expires_at=expires_at,
    )
    
    if applicable_product_ids:
        # Solo asociar productos que pertenecen al vendedor
        result = await db.execute(
            select(Product).where(
                Product.id.in_(applicable_product_ids),
                Product.seller_id == seller_id
            )
        )
        products = result.scalars().all()
        coupon.applicable_products = list(products)

    db.add(coupon)
    await db.flush()
    num_products = len(applicable_product_ids) if applicable_product_ids else 0
    logger.info("Cupón creado: %s por seller=%s con %d productos asociados", 
                code, seller_id, num_products)
    return coupon


async def list_coupons_by_seller(
    db: AsyncSession, seller_id: uuid.UUID
) -> Sequence[Coupon]:
    """Lista los cupones de un vendedor."""
    result = await db.execute(
        select(Coupon)
        .options(selectinload(Coupon.applicable_products))
        .where(Coupon.seller_id == seller_id)
        .order_by(Coupon.created_at.desc())
    )
    return result.scalars().all()


async def validate_coupon(
    db: AsyncSession,
    code: str,
    seller_id: uuid.UUID,
    subtotal: float,
    product_id: uuid.UUID | None = None,
) -> dict:
    """Valida un cupón y calcula el descuento.

    El cupón debe pertenecer al vendedor del producto y estar activo.
    """
    result = await db.execute(
        select(Coupon)
        .options(selectinload(Coupon.applicable_products))
        .where(
            Coupon.code == code.upper(),
            Coupon.seller_id == seller_id,
        )
    )
    coupon = result.scalar_one_or_none()

    if not coupon:
        return {
            "valid": False,
            "code": code,
            "discount_amount": 0.0,
            "message": "Cupón no encontrado para este vendedor",
        }

    if not coupon.is_valid():
        return {
            "valid": False,
            "code": code,
            "discount_amount": 0.0,
            "message": "Cupón expirado, agotado o inactivo",
        }

    # Validar restricción de producto
    if coupon.applicable_products:
        if not product_id or product_id not in [p.id for p in coupon.applicable_products]:
            return {
                "valid": False,
                "code": code,
                "discount_amount": 0.0,
                "message": "Este cupón no es válido para este producto",
            }

    discount = coupon.calculate_discount(subtotal)
    return {
        "valid": True,
        "code": code.upper(),
        "discount_amount": discount,
        "message": f"Descuento de ${discount:,.0f} COP aplicado",
    }


async def redeem_coupon(db: AsyncSession, code: str) -> None:
    """Incrementa el contador de uso del cupón."""
    result = await db.execute(select(Coupon).where(Coupon.code == code.upper()))
    coupon = result.scalar_one_or_none()
    if coupon:
        coupon.current_uses += 1
        await db.flush()


async def update_coupon(
    db: AsyncSession,
    coupon_id: uuid.UUID,
    seller_id: uuid.UUID,
    is_active: bool | None = None,
    max_uses: int | None = None,
    expires_at=None,
) -> Coupon:
    """Actualiza un cupón existente (solo el dueño)."""
    result = await db.execute(
        select(Coupon).where(Coupon.id == coupon_id, Coupon.seller_id == seller_id)
    )
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado",
        )
    if is_active is not None:
        coupon.is_active = is_active
    if max_uses is not None:
        coupon.max_uses = max_uses
    if expires_at is not None:
        coupon.expires_at = expires_at
    await db.flush()
    return coupon


async def delete_coupon(
    db: AsyncSession,
    coupon_id: uuid.UUID,
    seller_id: uuid.UUID,
) -> None:
    """Elimina un cupón (solo el dueño)."""
    result = await db.execute(
        select(Coupon).where(Coupon.id == coupon_id, Coupon.seller_id == seller_id)
    )
    coupon = result.scalar_one_or_none()
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado",
        )
    await db.delete(coupon)
    await db.flush()
