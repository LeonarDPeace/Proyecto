"""Tests — Analytics (HU 8.7).

Verifica el dashboard financiero.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app


async def override_get_db():
    yield AsyncMock()


@pytest.mark.asyncio
async def test_get_analytics_summary():
    """GET /api/v1/analytics/summary obtiene el resumen financiero."""
    user_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.analytics.analytics_service.get_seller_summary",
        new_callable=AsyncMock,
    ) as mock_summary:
        mock_summary.return_value = {
            "seller_id": user_id,
            "period": "month",
            "total_transactions": 5,
            "total_revenue_cop": 100000.0,
            "total_discount_cop": 5000.0,
            "net_revenue_cop": 95000.0,
            "average_order_cop": 20000.0,
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/analytics/summary", params={"period": "month"}
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["net_revenue_cop"] == 95000.0


@pytest.mark.asyncio
async def test_get_analytics_timeline():
    """GET /api/v1/analytics/timeline obtiene la línea de tiempo."""
    user_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = lambda: MagicMock(id=user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.analytics.analytics_service.get_seller_timeline",
        new_callable=AsyncMock,
    ) as mock_timeline:
        mock_timeline.return_value = [
            {"date": "2023-10-01", "revenue_cop": 50000.0, "transaction_count": 2},
            {"date": "2023-10-02", "revenue_cop": 45000.0, "transaction_count": 3},
        ]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/analytics/timeline", params={"period": "month"}
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["revenue_cop"] == 50000.0
