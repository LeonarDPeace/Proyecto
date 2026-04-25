import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services import product_service


@pytest.mark.asyncio
async def test_create_product_logic():
    db = AsyncMock()
    data = ProductCreate(
        name="Test Product",
        description="A great product",
        price=1000.0,
        category="Moda",
        image_urls=["http://example.com/image.jpg"],
    )
    product = await product_service.create_product(db, seller_id=uuid.uuid4(), data=data)
    assert product.name == "Test Product"
    assert db.add.called


@pytest.mark.asyncio
async def test_get_product_logic_not_found():
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    with pytest.raises(HTTPException) as exc:
        await product_service.get_product_by_id(db, uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_product_forbidden():
    db = AsyncMock()
    seller_id = uuid.uuid4()
    other_id = uuid.uuid4()
    
    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = seller_id
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result
    
    with pytest.raises(HTTPException) as exc:
        await product_service.update_product(
            db, uuid.uuid4(), other_id, ProductUpdate(name="New Name")
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_toggle_product_status_logic():
    db = AsyncMock()
    seller_id = uuid.uuid4()
    
    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = seller_id
    fake_product.is_active = True
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result
    
    product = await product_service.toggle_product_status(db, uuid.uuid4(), seller_id)
    assert product.is_active is False
    assert db.flush.called


@pytest.mark.asyncio
async def test_soft_delete_logic():
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
    assert db.flush.called
