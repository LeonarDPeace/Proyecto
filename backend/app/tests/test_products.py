"""Tests — Products endpoints (stubs Sprint 0)."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_products_returns_empty_list():
    """GET /api/v1/products/ debe retornar lista vacía (Sprint 0 stub)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products/")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_product_stub():
    """POST /api/v1/products/ debe aceptar producto válido (stub)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/products/",
            json={
                "name": "Almuerzo Casero",
                "price": 8000,
                "category": "comida",
            },
        )

    assert response.status_code == 201
    assert "Almuerzo Casero" in response.json()["message"]
