"""Tests — Coupons (HU 8.9).

Verifica CRUD y validación de cupones.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.coupon import Coupon
from app.models.user import User


def _mock_user(user_id: uuid.UUID | None = None, role: str = "vendedor") -> User:
    u = MagicMock(spec=User)
    u.id = user_id or uuid.uuid4()
    u.role = role
    return u


async def override_get_db():
    yield AsyncMock()


@pytest.mark.asyncio
async def test_create_coupon():
    """POST /api/v1/coupons/ crea un cupón."""
    seller_id = uuid.uuid4()
    fake_coupon = MagicMock(spec=Coupon)
    fake_coupon.id = uuid.uuid4()
    fake_coupon.seller_id = seller_id
    fake_coupon.code = "DESC10"
    fake_coupon.discount_percent = 10.0
    fake_coupon.discount_fixed_cop = None
    fake_coupon.max_uses = 10
    fake_coupon.current_uses = 0
    fake_coupon.is_active = True
    fake_coupon.expires_at = None
    fake_coupon.created_at = datetime.now(UTC)

    app.dependency_overrides[get_current_user] = lambda: _mock_user(seller_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.coupons.coupon_service.create_coupon", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = fake_coupon
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coupons/",
                json={"code": "DESC10", "discount_percent": 10.0, "max_uses": 10},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["code"] == "DESC10"


@pytest.mark.asyncio
async def test_create_coupon_forbidden_for_buyer():
    """Un comprador no puede crear cupones."""
    buyer_id = uuid.uuid4()
    app.dependency_overrides[get_current_user] = lambda: _mock_user(buyer_id, role="comprador")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/coupons/",
            json={"code": "DESC10", "discount_percent": 10.0},
        )
    
    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_validate_coupon():
    """GET /api/v1/coupons/validate valida un cupón."""
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.coupons.coupon_service.validate_coupon", new_callable=AsyncMock
    ) as mock_val:
        mock_val.return_value = {
            "valid": True,
            "code": "DESC10",
            "discount_amount": 5000.0,
            "message": "Descuento aplicado",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coupons/validate",
                params={"code": "DESC10", "seller_id": str(uuid.uuid4()), "subtotal": 50000},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["discount_amount"] == 5000.0
