"""Tests — Auth OTP flow (Sprint 1, HU 1.1 / HU 1.2).

Verifica:
- Solicitud de OTP con email válido e inválido.
- Verificación de OTP y generación de token JWT.
- Completar perfil de usuario nuevo.
- Actualizar perfil existente.
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
# OTP Request (HU 1.1)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_otp_request_valid_email():
    """POST /api/v1/auth/otp/request — email institucional válido."""
    with (
        patch("app.routers.auth.create_otp", new_callable=AsyncMock) as mock_create,
        patch("app.routers.auth.send_otp_email", new_callable=AsyncMock),
    ):
        mock_otp = MagicMock()
        mock_otp.code = "123456"
        mock_create.return_value = mock_otp

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/otp/request",
                json={"email": "student@uao.edu.co"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student@uao.edu.co"
    assert "expires_in_minutes" in data
    assert data["message"] == "Código OTP enviado al correo"


@pytest.mark.asyncio
async def test_otp_request_any_valid_email():
    """POST /api/v1/auth/otp/request — cualquier email válido → 200."""
    with (
        patch("app.routers.auth.create_otp", new_callable=AsyncMock) as mock_create,
        patch("app.routers.auth.send_otp_email", new_callable=AsyncMock),
    ):
        mock_otp = MagicMock()
        mock_otp.code = "123456"
        mock_create.return_value = mock_otp

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/otp/request",
                json={"email": "usuario@gmail.com"},
            )

    assert response.status_code == 200

@pytest.mark.asyncio
async def test_otp_request_invalid_email_format():
    """POST /api/v1/auth/otp/request — formato de email inválido → 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/otp/request",
            json={"email": "not-an-email"},
        )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# OTP Verify (HU 1.1)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_otp_verify_existing_user():
    """POST /api/v1/auth/otp/verify — usuario existente → token + is_new_user=false."""
    fake_user = _make_user()

    with (
        patch("app.routers.auth.verify_otp", new_callable=AsyncMock, return_value=True),
        patch(
            "app.routers.auth.get_user_by_email",
            new_callable=AsyncMock,
            return_value=fake_user,
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/otp/verify",
                json={"email": "test@uao.edu.co", "code": "123456"},
            )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["is_new_user"] is False


@pytest.mark.asyncio
async def test_otp_verify_new_user():
    """POST /api/v1/auth/otp/verify — usuario nuevo → token + is_new_user=true."""
    fake_user = _make_user(email="new@uao.edu.co")

    with (
        patch("app.routers.auth.verify_otp", new_callable=AsyncMock, return_value=True),
        patch(
            "app.routers.auth.get_user_by_email",
            new_callable=AsyncMock,
            return_value=None,
        ),
        patch(
            "app.routers.auth.create_user",
            new_callable=AsyncMock,
            return_value=fake_user,
        ),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/otp/verify",
                json={"email": "new@uao.edu.co", "code": "654321"},
            )

    assert response.status_code == 200
    data = response.json()
    assert data["is_new_user"] is True
    assert "access_token" in data


@pytest.mark.asyncio
async def test_otp_verify_invalid_code():
    """POST /api/v1/auth/otp/verify — código incorrecto → 401."""
    with patch(
        "app.routers.auth.verify_otp",
        new_callable=AsyncMock,
        return_value=False,
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/otp/verify",
                json={"email": "user@uao.edu.co", "code": "000000"},
            )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_otp_verify_bad_code_format():
    """POST /api/v1/auth/otp/verify — código no numérico → 422."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/otp/verify",
            json={"email": "user@uao.edu.co", "code": "abcdef"},
        )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Profile complete (HU 1.2)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_profile_success():
    """POST /api/v1/auth/profile/complete — perfil completado correctamente."""
    fake_user = _make_user(
        name="Nuevo Usuario",
        institutional_id="2210099",
    )

    with patch(
        "app.services.auth_service.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ), patch(
        "app.routers.auth.update_user_profile",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/profile/complete",
                json={
                    "name": "Nuevo Usuario",
                    "institutional_id": "2210099",
                    "accept_terms": True,
                },
                headers=headers,
            )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Nuevo Usuario"


@pytest.mark.asyncio
async def test_complete_profile_without_auth():
    """POST /api/v1/auth/profile/complete — sin token → 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/profile/complete",
            json={
                "name": "Sin Auth",
                "institutional_id": "0000000",
                "accept_terms": True,
            },
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_complete_profile_without_terms():
    """POST /api/v1/auth/profile/complete — sin aceptar T&C → 422."""
    fake_user = _make_user()

    with patch(
        "app.services.auth_service.get_user_by_id",
        new_callable=AsyncMock,
        return_value=fake_user,
    ):
        headers = _auth_header(user_id=fake_user.id)
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/profile/complete",
                json={
                    "name": "User",
                    "institutional_id": "2210099",
                    "accept_terms": False,
                },
                headers=headers,
            )

    assert response.status_code == 422
