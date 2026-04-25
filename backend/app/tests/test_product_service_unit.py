"""Tests — Product Service logic (HU 3.1-3.3).

Asegura cobertura > 80% en app/services/product_service.py.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import product_service


@pytest.mark.asyncio
async def test_create_product_logic():
    """Crea producto en la sesión."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    data = ProductCreate(
        name="Test", 
        description="Desc", 
        price=100.0, 
        category="Ropa"
    )

    product = await product_service.create_product(db, seller_id, data)
    assert product.name == "Test"
    assert db.add.called


@pytest.mark.asyncio
async def test_get_product_logic_not_found():
    """Lanza 404 si no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await product_service.get_product_by_id(db, uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_product_forbidden():
    """Lanza 403 si no es el dueño."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    other_id = uuid.uuid4()
    
    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = other_id
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result

    data = ProductUpdate(name="New Name")
    with pytest.raises(HTTPException) as exc:
        await product_service.update_product(db, uuid.uuid4(), seller_id, data)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_toggle_product_status_logic():
    """Cambia el estado del producto."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    
    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = seller_id
    fake_product.is_active = True
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result

    await product_service.toggle_product_status(db, uuid.uuid4(), seller_id)
    assert fake_product.is_active is False


@pytest.mark.asyncio
async def test_soft_delete_logic():
    """Marca como eliminado."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    
    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = seller_id
    fake_product.is_deleted = False
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result

    await product_service.soft_delete_product(db, uuid.uuid4(), seller_id)
    assert fake_product.is_deleted is True
