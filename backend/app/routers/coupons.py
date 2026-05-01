"""Router — Coupons (Cupones de descuento).

Sprint 5 — EP-08: Gestión Avanzada de Pedidos.
HU 8.9: Sistema de Cupones de Descuento.
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.coupon import CouponCreate, CouponRead, CouponUpdate, CouponValidation
from app.schemas.response import MessageResponse
from app.services import coupon_service

router = APIRouter()


@router.post(
    "/",
    response_model=CouponRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_coupon(
    data: CouponCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CouponRead:
    """Crea un nuevo cupón de descuento (solo vendedores)."""
    if current_user.role != "vendedor":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los vendedores pueden crear cupones",
        )

    coupon = await coupon_service.create_coupon(
        db,
        seller_id=current_user.id,
        code=data.code,
        discount_percent=data.discount_percent,
        discount_fixed_cop=data.discount_fixed_cop,
        max_uses=data.max_uses,
        expires_at=data.expires_at,
    )
    await db.commit()
    await db.refresh(coupon)
    return coupon


@router.get("/mine", response_model=list[CouponRead])
async def list_my_coupons(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CouponRead]:
    """Lista los cupones del vendedor autenticado."""
    return list(await coupon_service.list_coupons_by_seller(db, current_user.id))


@router.get("/validate", response_model=CouponValidation)
async def validate_coupon(
    code: str = Query(..., description="Código del cupón"),
    seller_id: uuid.UUID = Query(..., description="ID del vendedor"),
    subtotal: float = Query(..., gt=0, description="Subtotal del pedido en COP"),
    db: AsyncSession = Depends(get_db),
) -> CouponValidation:
    """Valida un cupón y calcula el descuento aplicable."""
    return await coupon_service.validate_coupon(db, code, seller_id, subtotal)


@router.put("/{coupon_id}", response_model=CouponRead)
async def update_coupon(
    coupon_id: uuid.UUID,
    data: CouponUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CouponRead:
    """Actualiza un cupón existente (solo el dueño)."""
    coupon = await coupon_service.update_coupon(
        db,
        coupon_id=coupon_id,
        seller_id=current_user.id,
        is_active=data.is_active,
        max_uses=data.max_uses,
        expires_at=data.expires_at,
    )
    await db.commit()
    await db.refresh(coupon)
    return coupon


@router.delete("/{coupon_id}", response_model=MessageResponse)
async def delete_coupon(
    coupon_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Elimina un cupón (solo el dueño)."""
    await coupon_service.delete_coupon(db, coupon_id, current_user.id)
    await db.commit()
    return MessageResponse(message="Cupón eliminado exitosamente")
