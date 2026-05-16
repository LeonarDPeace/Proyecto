"""Tests — Typesense Service.

Cobertura de:
- ensure_products_collection
- upsert_product_document
- delete_product_document
- search_products
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typesense.exceptions import ObjectAlreadyExists, ObjectNotFound

from app.models.product import Product
from app.services import typesense_service

@pytest.fixture
def mock_settings():
    with patch("app.services.typesense_service.settings") as mock:
        mock.TYPESENSE_API_KEY = "test_key"
        mock.TYPESENSE_COLLECTION_PRODUCTS = "test_products"
        yield mock

@pytest.fixture
def mock_typesense_client():
    client_mock = MagicMock()
    # Para upsert y delete
    client_mock.collections.__getitem__.return_value.documents.upsert = MagicMock()
    client_mock.collections.__getitem__.return_value.documents.__getitem__.return_value.delete = MagicMock()
    # Para search
    client_mock.collections.__getitem__.return_value.documents.search.return_value = {
        "hits": [{"document": {"id": "1", "name": "prod1"}}],
        "found": 1
    }
    with patch("app.services.typesense_service._get_client", return_value=client_mock):
        yield client_mock

@pytest.mark.asyncio
async def test_ensure_products_collection_success(mock_settings, mock_typesense_client):
    """Crea la colección correctamente."""
    await typesense_service.ensure_products_collection()
    assert mock_typesense_client.collections.create.called

@pytest.mark.asyncio
async def test_ensure_products_collection_already_exists(mock_settings, mock_typesense_client):
    """Maneja el error cuando la colección ya existe."""
    mock_typesense_client.collections.create.side_effect = ObjectAlreadyExists()
    await typesense_service.ensure_products_collection()
    assert mock_typesense_client.collections.create.called

@pytest.mark.asyncio
async def test_ensure_products_collection_no_api_key(mock_settings, mock_typesense_client):
    """No hace nada si no hay API key."""
    mock_settings.TYPESENSE_API_KEY = None
    await typesense_service.ensure_products_collection()
    assert not mock_typesense_client.collections.create.called

@pytest.mark.asyncio
async def test_upsert_product_document_success(mock_settings, mock_typesense_client):
    """Inserta o actualiza un documento correctamente."""
    db = AsyncMock()
    product = MagicMock(spec=Product)
    product.id = uuid.uuid4()
    product.seller_id = uuid.uuid4()
    product.name = "Test Product"
    product.description = "Test Desc"
    product.category = "Test Cat"
    product.subcategory = "Test Sub"
    product.condition = "nuevo"
    product.brand = "Test Brand"
    product.has_free_shipping = True
    product.image_urls = []
    product.price = 100.0
    product.is_active = True
    product.is_deleted = False
    product.created_at = datetime.now(UTC)
    product.updated_at = datetime.now(UTC)
    product.stock = 10
    product.discount_percentage = 0.0
    product.warranty_days = 0
    product.is_returnable = False
    product.fulfillment_type = "merchant"
    product.payment_methods = []
    product.promotions = []
    
    with patch("app.services.typesense_service._get_seller_info", new_callable=AsyncMock) as mock_info:
        mock_info.return_value = (None, None, None, 0.0)
        await typesense_service.upsert_product_document(db, product)
    
    assert mock_typesense_client.collections.__getitem__.return_value.documents.upsert.called

@pytest.mark.asyncio
async def test_upsert_product_document_no_api_key(mock_settings, mock_typesense_client):
    """No hace nada si no hay API key."""
    mock_settings.TYPESENSE_API_KEY = None
    db = AsyncMock()
    await typesense_service.upsert_product_document(db, MagicMock())
    assert not mock_typesense_client.collections.__getitem__.return_value.documents.upsert.called

@pytest.mark.asyncio
async def test_delete_product_document_success(mock_settings, mock_typesense_client):
    """Elimina el documento correctamente."""
    await typesense_service.delete_product_document(uuid.uuid4())
    assert mock_typesense_client.collections.__getitem__.return_value.documents.__getitem__.return_value.delete.called

@pytest.mark.asyncio
async def test_delete_product_document_not_found(mock_settings, mock_typesense_client):
    """Maneja el error si el documento no existe."""
    mock_typesense_client.collections.__getitem__.return_value.documents.__getitem__.return_value.delete.side_effect = ObjectNotFound()
    await typesense_service.delete_product_document(uuid.uuid4())
    assert mock_typesense_client.collections.__getitem__.return_value.documents.__getitem__.return_value.delete.called

@pytest.mark.asyncio
async def test_delete_product_document_no_api_key(mock_settings, mock_typesense_client):
    """No hace nada si no hay API key."""
    mock_settings.TYPESENSE_API_KEY = None
    await typesense_service.delete_product_document(uuid.uuid4())
    assert not mock_typesense_client.collections.__getitem__.return_value.documents.__getitem__.return_value.delete.called

@pytest.mark.asyncio
async def test_search_products_success(mock_settings, mock_typesense_client):
    """Busca productos y aplica filtros."""
    documents, found = await typesense_service.search_products(
        query_text="camisa",
        category="Ropa",
        min_price=10.0,
        max_price=100.0,
        availability="in_stock",
        tags=["verano"],
        payment_methods=["efectivo"],
        lat=3.35,
        lng=-76.53,
        radius_meters=1000
    )
    
    assert found == 1
    assert len(documents) == 1
    assert documents[0]["name"] == "prod1"
    assert mock_typesense_client.collections.__getitem__.return_value.documents.search.called
