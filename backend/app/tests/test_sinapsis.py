"""Tests — Vendor Role Request (HU 1.4, HU 1.5).

Verifica:
- Solicitud de rol vendedor con código Sinapsis válido.
- Solicitud de rol vendedor con código Sinapsis inválido.
- Solicitud de rol vendedor cuando ya es vendedor.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from httpx import ASGITransport, AsyncClient

from app.core.security import create_access_token
from app.main import app
from app.models.user import User

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_user(**overrides) -> User:
    """Crea un mock de User con valores por defecto."""
    defaults = {
        "id": uuid.uuid4(),
        "name": "Test User",
        "email": "test@uao.edu.co",
        "institutional_id": "2210001",
        "role": "comprador",
        "vendor_status": "pending",
        "reputation": 0.0,
        "is_verified": True,
        "phone": None,
        "show_email": False,
        "show_phone": False,
        "accepted_terms_at": datetime.now(UTC),
        "created_at": datetime.now(UTC),
    }
    defaults.update(overrides)
    user = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


def _auth_header(user_id: uuid.UUID | None = None, role: str = "comprador") -> dict:
    """Genera un header Authorization Bearer con un JWT válido."""
    uid = user_id or uuid.uuid4()
    token = create_access_token(data={"sub": str(uid), "role": role})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_vendor_request_valid_code():
    """POST /api/v1/auth/vendor/request — código Sinapsis válido."""
    fake_user = _make_user()

    with (
        patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock, return_value=fake_user),
        patch("app.routers.auth.request_vendor_role", new_callable=AsyncMock, return_value=("approved", "vendedor")),
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/vendor/request",
                json={"sinapsis_code": "SINAPSIS-TEST-001"},
                headers=headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Solicitud procesada correctamente."
    assert data["vendor_status"] == "approved"
    assert data["role"] == "vendedor"


@pytest.mark.asyncio
async def test_vendor_request_invalid_code():
    """POST /api/v1/auth/vendor/request — código Sinapsis inválido."""
    fake_user = _make_user()

    # Simulamos el HTTPException que arroja request_vendor_role
    def rise_exc(*args, **kwargs):
        raise HTTPException(status_code=400, detail="Código Sinapsis inválido o inactivo.")

    with (
        patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock, return_value=fake_user),
        patch("app.routers.auth.request_vendor_role", new_callable=AsyncMock, side_effect=rise_exc),
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/vendor/request",
                json={"sinapsis_code": "INVALID-CODE"},
                headers=headers,
            )

    assert response.status_code == 400
    assert response.json()["detail"] == "Código Sinapsis inválido o inactivo."


@pytest.mark.asyncio
async def test_vendor_request_already_vendor():
    """POST /api/v1/auth/vendor/request — ya tiene rol vendedor o status aprobado."""
    fake_user = _make_user(role="vendedor", vendor_status="approved")

    def rise_exc(*args, **kwargs):
        raise HTTPException(status_code=400, detail="El usuario ya tiene el rol de vendedor aprobado.")

    with (
        patch("app.services.auth_service.get_user_by_id", new_callable=AsyncMock, return_value=fake_user),
        patch("app.routers.auth.request_vendor_role", new_callable=AsyncMock, side_effect=rise_exc),
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/vendor/request",
                json={"sinapsis_code": "ANY-CODE"},
                headers=headers,
            )

    assert response.status_code == 400
    assert response.json()["detail"] == "El usuario ya tiene el rol de vendedor aprobado."
