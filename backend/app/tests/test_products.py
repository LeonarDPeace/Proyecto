"""Tests — Products endpoints (CRUD completo Sprint 1)."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.user import User

# --- Helpers ---


def _mock_user(user_id: uuid.UUID | None = None, role: str = "vendedor") -> User:
    """Mock User dependiente para saltar verificación de JWT/DB."""
    u = MagicMock(spec=User)
    u.id = user_id or uuid.uuid4()
    u.role = role
    u.vendor_status = "approved" if role == "vendedor" else "pending"
    return u


def _make_product_dict(id=None, seller_id=None, **overrides) -> dict:
    """Retorna un dict serializable de ProductRead."""
    prod = {
        "id": str(id or uuid.uuid4()),
        "seller_id": str(seller_id or uuid.uuid4()),
        "name": "Hamburguesa Casera",
        "description": "Muy rica",
        "price": 15000.0,
        "category": "comida",
        "image_urls": ["https://ejemplo.com/1.jpg"],
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    prod.update(overrides)
    return prod


class MockProduct:
    """Simula un objeto Product ORM antes de la serialización pydantic."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


async def override_get_db():
    yield AsyncMock()


# --- Tests ---


@pytest.mark.asyncio
async def test_list_products():
    """GET /api/v1/products/ retorna lista y soporta paginación."""
    fake_db_products = [MockProduct(**_make_product_dict()), MockProduct(**_make_product_dict())]

    with patch("app.routers.products.product_service.list_products", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = fake_db_products
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/products/?limit=2")

    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_list.assert_called_once()


@pytest.mark.asyncio
async def test_get_product_success():
    """GET /api/v1/products/{id} retorna 1 producto."""
    prod_id = uuid.uuid4()
    fake_prod = MockProduct(**_make_product_dict(id=prod_id))

    with patch("app.routers.products.product_service.get_product_by_id", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = fake_prod
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/products/{prod_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(prod_id)


@pytest.mark.asyncio
async def test_create_product_vendedor():
    """POST /api/v1/products/ crea producto si es vendedor."""
    seller_id = uuid.uuid4()
    fake_prod = MockProduct(**_make_product_dict(seller_id=seller_id, name="Empanada", price=2500.0))

    app.dependency_overrides[get_current_user] = lambda: _mock_user(seller_id, role="vendedor")
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.routers.products.product_service.create_product", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = fake_prod
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/products/", json={"name": "Empanada", "price": 2500, "category": "comida"}
            )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["name"] == "Empanada"
    assert response.json()["price"] == 2500.0


@pytest.mark.asyncio
async def test_create_product_comprador_forbidden():
    """POST /api/v1/products/ retorna 403 si el rol es comprador."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user(role="comprador")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/products/", json={"name": "Empanada", "price": 2500})

    app.dependency_overrides.clear()
    assert response.status_code == 403
    assert "vendedores" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_product_invalid_price():
    """POST /api/v1/products/ valida precio > 0 (Pydantic)."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user(role="vendedor")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/products/", json={"name": "Mal Precio", "price": -500})

    app.dependency_overrides.clear()
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_product_max_images():
    """POST /api/v1/products/ lanza 422 si hay más de 5 imágenes."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user(role="vendedor")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/products/",
            json={"name": "Fotos Extra", "price": 1000, "image_urls": ["url1", "url2", "url3", "url4", "url5", "url6"]},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_update_product_success():
    """PUT /api/v1/products/{id} actualiza un producto si le pertenece."""
    prod_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    fake_prod = MockProduct(**_make_product_dict(id=prod_id, seller_id=seller_id, name="Nombre Actualizado"))

    app.dependency_overrides[get_current_user] = lambda: _mock_user(seller_id, role="vendedor")
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.routers.products.product_service.update_product", new_callable=AsyncMock) as mock_upd:
        mock_upd.return_value = fake_prod
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                f"/api/v1/products/{prod_id}", json={"name": "Nombre Actualizado", "price": 3000}
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["name"] == "Nombre Actualizado"


@pytest.mark.asyncio
async def test_delete_product():
    """DELETE /api/v1/products/{id} retorna confirmación de soft-delete."""
    prod_id = uuid.uuid4()
    seller_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: _mock_user(seller_id, role="vendedor")
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.routers.products.product_service.soft_delete_product", new_callable=AsyncMock):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete(f"/api/v1/products/{prod_id}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert "exitosamente" in response.json()["message"]


@pytest.mark.asyncio
async def test_toggle_status_product():
    """PATCH /api/v1/products/{id}/status alterna is_active."""
    prod_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    fake_prod = MockProduct(**_make_product_dict(id=prod_id, seller_id=seller_id, is_active=False))

    app.dependency_overrides[get_current_user] = lambda: _mock_user(seller_id, role="vendedor")
    app.dependency_overrides[get_db] = override_get_db

    with patch("app.routers.products.product_service.toggle_product_status", new_callable=AsyncMock) as mock_tog:
        mock_tog.return_value = fake_prod
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/api/v1/products/{prod_id}/status")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["is_active"] is False
