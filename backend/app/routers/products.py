"""Router — Products (CRUD del catálogo P2P).

HU 3.1: Crear producto.
HU 3.2: Actualizar / ver producto.
HU 3.3: Eliminar producto (soft-delete) y pausar.
"""

import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.schemas.response import MessageResponse
from app.services import product_service

router = APIRouter()


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
    return product
