"""Tests — Negotiation Service (lógica de negocio Sprint 4).

Cobertura de módulos de lógica de negocio para CI/CD pipeline (≥ 70%).
HU 6.1: Chat en tiempo real.
HU 6.2/6.3: Deep Links Nequi / DaviPlata.
HU 6.4: Confirmación de entrega.
HU 6.5: Registro GMV.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.user import User
from app.services.negotiation_service import generate_payment_deep_link


# --- Helpers ---


def _mock_user(user_id: uuid.UUID | None = None, role: str = "comprador") -> User:
    """Mock User para saltar verificación de JWT/DB."""
    u = MagicMock(spec=User)
    u.id = user_id or uuid.uuid4()
    u.role = role
    u.name = "Test User"
    u.phone = "3001234567"
    u.email = "test@uao.edu.co"
    u.vendor_status = "approved" if role == "vendedor" else "pending"
    return u


class MockNegotiation:
    """Simula un objeto Negotiation ORM."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockChatMessage:
    """Simula un objeto ChatMessage ORM."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _make_negotiation_dict(
    id=None, buyer_id=None, seller_id=None, product_id=None, **overrides
) -> dict:
    """Retorna un dict serializable de NegotiationRead."""
    neg = {
        "id": str(id or uuid.uuid4()),
        "buyer_id": str(buyer_id or uuid.uuid4()),
        "seller_id": str(seller_id or uuid.uuid4()),
        "product_id": str(product_id or uuid.uuid4()),
        "status": "pending",
        "buyer_confirmed": False,
        "seller_confirmed": False,
        "agreed_price_cop": 15000.0,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }
    neg.update(overrides)
    return neg


def _make_message_dict(
    id=None, negotiation_id=None, sender_id=None, **overrides
) -> dict:
    """Retorna un dict serializable de ChatMessageRead."""
    msg = {
        "id": str(id or uuid.uuid4()),
        "negotiation_id": str(negotiation_id or uuid.uuid4()),
        "sender_id": str(sender_id or uuid.uuid4()),
        "content": "Hola, me interesa tu producto",
        "created_at": datetime.now(UTC).isoformat(),
    }
    msg.update(overrides)
    return msg


async def override_get_db():
    yield AsyncMock()


# --- Tests: Negotiation CRUD ---


@pytest.mark.asyncio
async def test_create_negotiation():
    """POST /api/v1/negotiations/ crea una negociación."""
    buyer_id = uuid.uuid4()
    product_id = uuid.uuid4()
    fake_neg = MockNegotiation(
        **_make_negotiation_dict(buyer_id=buyer_id, product_id=product_id)
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(
        buyer_id, role="comprador"
    )
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.create_negotiation",
        new_callable=AsyncMock,
    ) as mock_create:
        mock_create.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/negotiations/",
                json={
                    "product_id": str(product_id),
                    "initial_message": "Me interesa tu producto",
                },
            )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["product_id"] == str(product_id)


@pytest.mark.asyncio
async def test_list_my_negotiations():
    """GET /api/v1/negotiations/ retorna lista de negociaciones del usuario."""
    user_id = uuid.uuid4()
    fake_negs = [
        MockNegotiation(**_make_negotiation_dict(buyer_id=user_id)),
        MockNegotiation(**_make_negotiation_dict(seller_id=user_id)),
    ]

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.list_negotiations_by_user",
        new_callable=AsyncMock,
    ) as mock_list:
        mock_list.return_value = fake_negs
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/negotiations/")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_get_negotiation_success():
    """GET /api/v1/negotiations/{id} retorna detalle de negociación."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MockNegotiation(
        **_make_negotiation_dict(id=neg_id, buyer_id=user_id)
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.get_negotiation_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/negotiations/{neg_id}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["id"] == str(neg_id)


@pytest.mark.asyncio
async def test_get_negotiation_forbidden():
    """GET /api/v1/negotiations/{id} retorna 403 si el usuario no es parte."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    # Negociación de otros usuarios
    fake_neg = MockNegotiation(**_make_negotiation_dict(id=neg_id))

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.get_negotiation_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/negotiations/{neg_id}")

    app.dependency_overrides.clear()
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_negotiation_status():
    """PATCH /api/v1/negotiations/{id}/status actualiza estado."""
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MockNegotiation(
        **_make_negotiation_dict(id=neg_id, seller_id=seller_id, status="accepted")
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(
        seller_id, role="vendedor"
    )
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.update_negotiation_status",
        new_callable=AsyncMock,
    ) as mock_update:
        mock_update.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(
                f"/api/v1/negotiations/{neg_id}/status",
                json={"status": "accepted"},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


# --- Tests: HU 6.4 — Confirmación de entrega ---


@pytest.mark.asyncio
async def test_confirm_delivery_buyer():
    """PATCH /api/v1/negotiations/{id}/confirm confirma entrega del comprador."""
    buyer_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MockNegotiation(
        **_make_negotiation_dict(
            id=neg_id,
            buyer_id=buyer_id,
            status="accepted",
            buyer_confirmed=True,
            seller_confirmed=False,
        )
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(buyer_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.confirm_delivery",
        new_callable=AsyncMock,
    ) as mock_confirm:
        mock_confirm.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/api/v1/negotiations/{neg_id}/confirm")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["buyer_confirmed"] is True


@pytest.mark.asyncio
async def test_confirm_delivery_both_completes():
    """Cuando ambas partes confirman, la negociación se completa."""
    buyer_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MockNegotiation(
        **_make_negotiation_dict(
            id=neg_id,
            buyer_id=buyer_id,
            status="completed",
            buyer_confirmed=True,
            seller_confirmed=True,
        )
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(buyer_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.confirm_delivery",
        new_callable=AsyncMock,
    ) as mock_confirm:
        mock_confirm.return_value = fake_neg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.patch(f"/api/v1/negotiations/{neg_id}/confirm")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["buyer_confirmed"] is True
    assert response.json()["seller_confirmed"] is True


# --- Tests: HU 6.1 — Chat Messages ---


@pytest.mark.asyncio
async def test_send_message():
    """POST /api/v1/negotiations/{id}/messages envía un mensaje."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_msg = MockChatMessage(
        **_make_message_dict(negotiation_id=neg_id, sender_id=user_id)
    )

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.create_chat_message",
        new_callable=AsyncMock,
    ) as mock_send:
        mock_send.return_value = fake_msg
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                f"/api/v1/negotiations/{neg_id}/messages",
                json={"content": "Hola, me interesa tu producto"},
            )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert "Hola" in response.json()["content"]


@pytest.mark.asyncio
async def test_list_messages():
    """GET /api/v1/negotiations/{id}/messages lista mensajes."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_msgs = [
        MockChatMessage(
            **_make_message_dict(negotiation_id=neg_id, sender_id=user_id)
        ),
        MockChatMessage(
            **_make_message_dict(negotiation_id=neg_id, sender_id=uuid.uuid4())
        ),
    ]

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.list_chat_messages",
        new_callable=AsyncMock,
    ) as mock_list:
        mock_list.return_value = fake_msgs
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/negotiations/{neg_id}/messages")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_send_message_empty_content():
    """POST /api/v1/negotiations/{id}/messages rechaza mensaje vacío."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/negotiations/{neg_id}/messages",
            json={"content": ""},
        )

    app.dependency_overrides.clear()
    assert response.status_code == 422


# --- Tests: HU 6.2/6.3 — Deep Links ---


def test_generate_nequi_deep_link():
    """Genera un deep link correcto para Nequi."""
    result = generate_payment_deep_link(
        platform="nequi",
        seller_phone="+573001234567",
        amount_cop=15000.0,
    )
    assert result["platform"] == "nequi"
    assert "nequi://" in result["deep_link_url"]
    assert "3001234567" in result["deep_link_url"]
    assert "15000" in result["deep_link_url"]


def test_generate_daviplata_deep_link():
    """Genera un deep link correcto para DaviPlata."""
    result = generate_payment_deep_link(
        platform="daviplata",
        seller_phone="3009876543",
        amount_cop=8500.0,
    )
    assert result["platform"] == "daviplata"
    assert "daviplata://" in result["deep_link_url"]
    assert "3009876543" in result["deep_link_url"]


def test_generate_deep_link_without_amount():
    """Genera deep link sin monto (solo número de teléfono)."""
    result = generate_payment_deep_link(
        platform="nequi",
        seller_phone="3001112233",
    )
    assert result["platform"] == "nequi"
    assert "amount" not in result["deep_link_url"]


def test_generate_deep_link_invalid_platform():
    """Plataforma no soportada lanza HTTPException."""
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc_info:
        generate_payment_deep_link(
            platform="bancolombia",
            seller_phone="3001234567",
        )
    assert exc_info.value.status_code == 400


# --- Tests: HU 6.5 — GMV Metrics ---


@pytest.mark.asyncio
async def test_get_gmv_summary():
    """GET /api/v1/negotiations/metrics/gmv retorna resumen GMV."""
    user_id = uuid.uuid4()

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.negotiations.negotiation_service.get_gmv_summary",
        new_callable=AsyncMock,
    ) as mock_gmv:
        mock_gmv.return_value = {
            "total_transactions": 42,
            "total_gmv_cop": 1_250_000.0,
            "period": "all_time",
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/negotiations/metrics/gmv")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 42
    assert data["total_gmv_cop"] == 1_250_000.0
