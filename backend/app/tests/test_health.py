"""Tests — Health Check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_ok():
    """GET /health debe retornar status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert "environment" in data


@pytest.mark.asyncio
async def test_health_check_has_correct_fields():
    """El response del health check debe tener los 3 campos esperados."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    data = response.json()
    expected_keys = {"status", "version", "environment"}
    assert set(data.keys()) == expected_keys
