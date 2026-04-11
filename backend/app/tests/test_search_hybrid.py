"""Tests — Búsqueda híbrida (Gemini + Typesense + fallback)."""

import uuid
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.main import app
from app.models.user import User
from app.services.nlu_service import NLUQueryResult
from app.services.quota_service import QuotaSnapshot


def _mock_user(user_id: uuid.UUID | None = None) -> User:
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.role = "comprador"
    return user


@pytest.mark.asyncio
async def test_search_unauthenticated_uses_fallback_mode():
    """Sin token, el endpoint debe buscar y marcar modo fallback_fulltext."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    document = {
        "id": str(uuid.uuid4()),
        "seller_id": str(uuid.uuid4()),
        "name": "Mecato Dulce",
        "description": "Snack para clase",
        "price": 5000,
        "category": "comida",
        "image_urls": [],
        "is_active": True,
    }

    with patch(
        "app.routers.products.typesense_service.search_products",
        new_callable=AsyncMock,
    ) as mock_search:
        mock_search.return_value = ([document], 1)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/products/search?q=mecato")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["search_mode"] == "fallback_fulltext"
    assert payload["meta"]["reason"] == "unauthenticated"
    assert len(payload["items"]) == 1


@pytest.mark.asyncio
async def test_search_authenticated_uses_semantic_when_quota_available():
    """Con cuota disponible y NLU válido, debe usar modo semantic y consumir cuota."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    user = _mock_user()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_optional] = lambda: user

    before_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=0,
        remaining=10,
    )
    after_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=1,
        remaining=9,
    )

    document = {
        "id": str(uuid.uuid4()),
        "seller_id": str(uuid.uuid4()),
        "name": "Brownie",
        "description": "Postre casero",
        "price": 7000,
        "category": "comida",
        "image_urls": [],
        "is_active": True,
    }

    with (
        patch(
            "app.routers.products.quota_service.get_quota_snapshot",
            new_callable=AsyncMock,
            return_value=before_snapshot,
        ),
        patch(
            "app.routers.products.quota_service.try_consume_semantic_search",
            new_callable=AsyncMock,
            return_value=(True, after_snapshot),
        ),
        patch(
            "app.routers.products.nlu_service.parse_semantic_query",
            new_callable=AsyncMock,
            return_value=NLUQueryResult(
                query_clean="dulce",
                tags=["snack", "postre"],
                category="comida",
            ),
        ),
        patch(
            "app.routers.products.typesense_service.search_products",
            new_callable=AsyncMock,
            return_value=([document], 1),
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/products/search?q=Busco%20algo%20dulce"
            )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["search_mode"] == "semantic"
    assert payload["meta"]["quota_remaining"] == 9
    assert payload["meta"]["query_clean"] == "dulce"
    mock_db.commit.assert_awaited()


@pytest.mark.asyncio
async def test_search_falls_back_to_postgres_if_typesense_fails():
    """Si Typesense falla, debe responder con fallback textual en PostgreSQL."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    fallback_product = SimpleNamespace(
        id=uuid.uuid4(),
        seller_id=uuid.uuid4(),
        name="Audífonos",
        description="Bluetooth",
        price=45000,
        category="tecnologia",
        image_urls=[],
        is_active=True,
    )

    with (
        patch(
            "app.routers.products.typesense_service.search_products",
            new_callable=AsyncMock,
            side_effect=RuntimeError("typesense down"),
        ),
        patch(
            "app.routers.products.product_service.search_products_text",
            new_callable=AsyncMock,
            return_value=[fallback_product],
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/products/search?q=audifonos")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["search_mode"] == "fallback_fulltext"
    assert payload["meta"]["reason"] == "unauthenticated"
    assert len(payload["items"]) == 1


@pytest.mark.asyncio
async def test_search_nlu_failure_does_not_consume_quota():
    """Si falla NLU, se hace fallback sin descontar cuota."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    user = _mock_user()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_optional] = lambda: user

    before_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=0,
        remaining=10,
    )
    after_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=1,
        remaining=9,
    )

    document = {
        "id": str(uuid.uuid4()),
        "seller_id": str(uuid.uuid4()),
        "name": "Galletas",
        "description": "Snack",
        "price": 4000,
        "category": "comida",
        "image_urls": [],
        "is_active": True,
    }

    with (
        patch(
            "app.routers.products.quota_service.get_quota_snapshot",
            new_callable=AsyncMock,
            return_value=before_snapshot,
        ),
        patch(
            "app.routers.products.quota_service.try_consume_semantic_search",
            new_callable=AsyncMock,
            return_value=(True, after_snapshot),
        ),
        patch(
            "app.routers.products.nlu_service.parse_semantic_query",
            new_callable=AsyncMock,
            side_effect=RuntimeError("gemini down"),
        ),
        patch(
            "app.routers.products.typesense_service.search_products",
            new_callable=AsyncMock,
            return_value=([document], 1),
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/products/search?q=algo")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["search_mode"] == "fallback_fulltext"
    assert payload["meta"]["reason"] == "nlu_failed"
    assert payload["meta"]["quota_remaining"] == 10
    mock_db.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_search_typesense_failure_after_semantic_does_not_consume_quota():
    """Si falla Typesense luego de NLU, se hace fallback sin descontar cuota."""
    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    user = _mock_user()
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_optional] = lambda: user

    before_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=0,
        remaining=10,
    )
    after_snapshot = QuotaSnapshot(
        business_date=date.today(),
        daily_limit=10,
        searches_used=1,
        remaining=9,
    )

    fallback_product = SimpleNamespace(
        id=uuid.uuid4(),
        seller_id=uuid.uuid4(),
        name="Brownie",
        description="Postre",
        price=6000,
        category="comida",
        image_urls=[],
        is_active=True,
    )

    with (
        patch(
            "app.routers.products.quota_service.get_quota_snapshot",
            new_callable=AsyncMock,
            return_value=before_snapshot,
        ),
        patch(
            "app.routers.products.quota_service.try_consume_semantic_search",
            new_callable=AsyncMock,
            return_value=(True, after_snapshot),
        ),
        patch(
            "app.routers.products.nlu_service.parse_semantic_query",
            new_callable=AsyncMock,
            return_value=NLUQueryResult(
                query_clean="brownie",
                tags=["postre"],
                category="comida",
            ),
        ),
        patch(
            "app.routers.products.typesense_service.search_products",
            new_callable=AsyncMock,
            side_effect=RuntimeError("typesense down"),
        ),
        patch(
            "app.routers.products.product_service.search_products_text",
            new_callable=AsyncMock,
            return_value=[fallback_product],
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/products/search?q=brownie")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["search_mode"] == "fallback_fulltext"
    assert payload["meta"]["reason"] == "typesense_unavailable"
    assert payload["meta"]["quota_remaining"] == 10
    mock_db.commit.assert_not_awaited()
