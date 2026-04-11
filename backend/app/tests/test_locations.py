"""Tests — Locations endpoints (setup de ubicación en perfil)."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.user import User


def _mock_user(role: str = "vendedor") -> User:
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.role = role
    return user


async def _override_get_db():
    yield AsyncMock()


@pytest.mark.asyncio
async def test_upsert_location_forbidden_for_comprador():
    """Solo vendedores pueden configurar ubicación."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user(role="comprador")
    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/locations/me",
            json={"lat": 3.35, "lng": -76.53, "campus": "UAO"},
        )

    app.dependency_overrides.clear()

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_upsert_location_success():
    """PUT /locations/me guarda ubicación y retorna coordenadas."""
    user = _mock_user(role="vendedor")
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_db] = _override_get_db

    saved = {
        "id": uuid.uuid4(),
        "user_id": user.id,
        "campus": "UAO",
        "label": "Biblioteca",
        "lat": 3.3516,
        "lng": -76.5320,
        "updated_at": datetime.now(UTC),
    }

    with (
        patch(
            "app.routers.locations.location_service.upsert_user_location",
            new_callable=AsyncMock,
            return_value=saved,
        ),
        patch(
            "app.routers.locations.product_service.list_products_by_seller",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                "/api/v1/locations/me",
                json={
                    "lat": 3.3516,
                    "lng": -76.5320,
                    "campus": "UAO",
                    "label": "Biblioteca",
                },
            )

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["campus"] == "UAO"
    assert payload["label"] == "Biblioteca"


@pytest.mark.asyncio
async def test_delete_location_success():
    """DELETE /locations/me elimina ubicación existente."""
    app.dependency_overrides[get_current_user] = lambda: _mock_user(role="vendedor")
    app.dependency_overrides[get_db] = _override_get_db

    with (
        patch(
            "app.routers.locations.location_service.delete_user_location",
            new_callable=AsyncMock,
            return_value=True,
        ),
        patch(
            "app.routers.locations.product_service.list_products_by_seller",
            new_callable=AsyncMock,
            return_value=[],
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.delete("/api/v1/locations/me")

    app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["deleted"] is True
