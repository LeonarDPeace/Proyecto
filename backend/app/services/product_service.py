"""Service — Lógica de negocio para Productos.

HU 3.1: Crear producto.
HU 3.2: Actualizar / ver producto.
HU 3.3: Soft-delete y pausar (toggle).
"""

import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def create_product(
    db: AsyncSession, seller_id: uuid.UUID, data: ProductCreate
) -> Product:
    """Crea un nuevo producto en BD (solo rol Vendedor)."""
    product = Product(
        seller_id=seller_id,
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        subcategory=data.subcategory,
        condition=data.condition,
        brand=data.brand,
        has_free_shipping=data.has_free_shipping,
        attributes=data.attributes,
        image_urls=data.image_urls,
    )
    db.add(product)
    await db.flush()
    return product


async def get_product_by_id(
    db: AsyncSession, product_id: uuid.UUID, active_only: bool = True
) -> Product:
    """Busca un producto por ID."""
    query = select(Product).where(Product.id == product_id, Product.is_deleted == False)  # noqa: E712
    if active_only:
        query = query.where(Product.is_active == True)  # noqa: E712

    result = await db.execute(query)
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return product


async def list_products(
    db: AsyncSession, category: str | None = None, limit: int = 20, offset: int = 0
) -> Sequence[Product]:
    """Obtiene productos activos (is_active=True) y no eliminados con paginación y filtros."""
    query = select(Product).where(
        Product.is_active == True, Product.is_deleted == False
    )  # noqa: E712

    if category:
        query = query.where(Product.category == category)

    query = query.order_by(Product.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


async def list_products_by_seller(
    db: AsyncSession, seller_id: uuid.UUID
) -> Sequence[Product]:
    """Obtiene TODOS los productos de un vendedor (incluyendo inactivos, pero excluyendo eliminados)."""
    query = (
        select(Product)
        .where(Product.seller_id == seller_id, Product.is_deleted == False)  # noqa: E712
        .order_by(Product.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


async def update_product(
    db: AsyncSession,
    product_id: uuid.UUID,
    seller_id: uuid.UUID,
    data: ProductUpdate,
) -> Product:
    """Actualiza un producto (solo el dueño puede hacerlo)."""
    # Se debe permitir editar productos inactivos (por ejemplo si estaban pausados)
    product = await get_product_by_id(db, product_id, active_only=False)

    if product.seller_id != seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este producto",
        )

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    await db.flush()
    return product


async def soft_delete_product(
    db: AsyncSession, product_id: uuid.UUID, seller_id: uuid.UUID
) -> None:
    """Aplica soft-delete (eliminación lógica)."""
    product = await get_product_by_id(db, product_id, active_only=False)

    if product.seller_id != seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar este producto",
        )

    product.is_deleted = True
    await db.flush()


async def toggle_product_status(
    db: AsyncSession, product_id: uuid.UUID, seller_id: uuid.UUID
) -> Product:
    """Alterna el estado is_active (Disponible/Agotado o Pausado)."""
    product = await get_product_by_id(db, product_id, active_only=False)

    if product.seller_id != seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para modificar este producto",
        )

    product.is_active = not product.is_active
    await db.flush()
    return product


async def search_products_text(
    db: AsyncSession,
    query_text: str,
    *,
    category: str | None = None,
    limit: int = 20,
) -> Sequence[Product]:
    """Fallback textual en PostgreSQL cuando no se puede usar Typesense."""
    query = select(Product).where(
        Product.is_active == True, Product.is_deleted == False
    )  # noqa: E712

    if category:
        query = query.where(Product.category == category)

    cleaned_query = query_text.strip()
    if cleaned_query and cleaned_query != "*":
        pattern = f"%{cleaned_query}%"
        query = query.where(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
                Product.category.ilike(pattern),
            )
        )

    query = query.order_by(Product.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
