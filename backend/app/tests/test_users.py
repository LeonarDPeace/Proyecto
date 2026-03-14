"""Tests — Users endpoints (Sprint 1, HU 1.2 / HU 1.3).

Verifica:
- GET /users/me — perfil privado (autenticado).
- GET /users/{user_id} — perfil público.
- GET /users/me/privacy — configuración de privacidad.
- PUT /users/me/privacy — actualizar privacidad.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
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
        "reputation": 0.0,
        "is_verified": True,
        "phone": "3001234567",
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
# GET /users/me — Perfil privado (HU 1.2)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_me_returns_private_profile():
    """GET /api/v1/users/me — usuario autenticado ve su perfil completo."""
    fake_user = _make_user()

    with patch(
        "app.services.auth_service.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@uao.edu.co"
    assert data["name"] == "Test User"
    assert data["institutional_id"] == "2210001"
    assert "show_email" in data
    assert "show_phone" in data


@pytest.mark.asyncio
async def test_get_me_without_auth():
    """GET /api/v1/users/me — sin token → 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_invalid_token():
    """GET /api/v1/users/me — token inválido → 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /users/{user_id} — Perfil público
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_user_public_profile():
    """GET /api/v1/users/{user_id} — perfil público visible."""
    fake_user = _make_user(show_email=False, show_phone=False)

    with patch(
        "app.routers.users.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{fake_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test User"
    assert data["role"] == "comprador"
    assert "is_verified" in data
    # HU 1.3: email y phone ocultos por defecto (Privacy by Design)
    assert data["email"] is None
    assert data["phone"] is None


@pytest.mark.asyncio
async def test_get_user_public_profile_shows_contact_when_allowed():
    """GET /api/v1/users/{user_id} — muestra contacto si privacidad lo permite."""
    fake_user = _make_user(
        show_email=True,
        show_phone=True,
        email="visible@uao.edu.co",
        phone="3009999999",
    )

    with patch(
        "app.routers.users.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{fake_user.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "visible@uao.edu.co"
    assert data["phone"] == "3009999999"


@pytest.mark.asyncio
async def test_get_user_not_found():
    """GET /api/v1/users/{user_id} — ID inexistente → 404."""
    random_id = uuid.uuid4()

    with patch(
        "app.routers.users.get_user_by_id",
        new_callable=AsyncMock,
        return_value=None,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/users/{random_id}")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Privacy settings (HU 1.3)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_privacy_settings():
    """GET /api/v1/users/me/privacy — retorna config de privacidad."""
    fake_user = _make_user(show_email=True, show_phone=False)

    with patch(
        "app.services.auth_service.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/users/me/privacy", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["show_email"] is True
    assert data["show_phone"] is False


@pytest.mark.asyncio
async def test_update_privacy_settings():
    """PUT /api/v1/users/me/privacy — actualiza config correctamente."""
    fake_user = _make_user(show_email=False, show_phone=False)
    updated_user = _make_user(show_email=True, show_phone=True)

    with (
        patch(
            "app.services.auth_service.get_user_by_id",
            new_callable=AsyncMock,
            return_value=fake_user,
        ),
        patch(
            "app.routers.users.update_user_profile",
            new_callable=AsyncMock,
            return_value=updated_user,
        ),
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.put(
                "/api/v1/users/me/privacy",
                json={"show_email": True, "show_phone": True},
                headers=headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["show_email"] is True
    assert data["show_phone"] is True


@pytest.mark.asyncio
async def test_update_privacy_without_auth():
    """PUT /api/v1/users/me/privacy — sin token → 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/v1/users/me/privacy",
            json={"show_email": True, "show_phone": True},
        )

    assert response.status_code == 401
