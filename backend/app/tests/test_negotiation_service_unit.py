"""Tests — Negotiation Service logic (HU 6.1-6.5).

Asegura cobertura > 90% en app/services/negotiation_service.py.

Fix: test_confirm_delivery_logic_flow — el mock del producto en _record_gmv
     debe tener .name y .price correctamente configurados.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.negotiation import Negotiation
from app.models.product import Product
from app.services import negotiation_service

# ---------------------------------------------------------------------------
# Create Negotiation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_negotiation_logic_success():
    """Valida creación exitosa de negociación."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    product_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.id = product_id
    fake_product.seller_id = seller_id
    fake_product.price = 10000.0
    fake_product.is_active = True
    fake_product.is_deleted = False

    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = fake_product

    mock_result_existing = MagicMock()
    mock_result_existing.scalar_one_or_none.return_value = None

    db.execute.side_effect = [mock_result_product, mock_result_existing]

    neg = await negotiation_service.create_negotiation(
        db, buyer_id, product_id, initial_message="Hola"
    )

    assert neg.buyer_id == buyer_id
    assert neg.seller_id == seller_id
    assert db.add.call_count == 2  # Negotiation + ChatMessage


@pytest.mark.asyncio
async def test_create_negotiation_product_not_found():
    """Lanza 404 si el producto no existe o está inactivo."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_negotiation(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_create_negotiation_self_purchase():
    """Lanza 400 si el comprador es el mismo vendedor."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = buyer_id

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_negotiation(db, buyer_id, uuid.uuid4())
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# Confirm Delivery — FIXED: mock producto con .name y .price para _record_gmv
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confirm_delivery_logic_flow():
    """Valida flujo de confirmación dual y cierre con registro GMV."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    product_id = uuid.uuid4()

    # --- Negotiation mock ---
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.id = neg_id
    fake_neg.buyer_id = buyer_id
    fake_neg.seller_id = seller_id
    fake_neg.status = "accepted"
    fake_neg.buyer_confirmed = False
    fake_neg.seller_confirmed = False
    fake_neg.product_id = product_id
    fake_neg.agreed_price_cop = 5000.0
    fake_neg.transaction_locked = True
    fake_neg.coupon_code = None
    fake_neg.quantity = 1

    # --- Product mock (para _record_gmv) ---
    fake_product = MagicMock(spec=Product)
    fake_product.name = "Camiseta de Prueba"
    fake_product.price = 5000.0

    # DB devuelve la negociación en todas las consultas de negociación,
    # y el producto cuando _record_gmv lo consulta.
    mock_result_neg = MagicMock()
    mock_result_neg.scalar_one_or_none.return_value = fake_neg

    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = fake_product

    # Primera llamada → negociación (buyer confirm)
    db.execute.side_effect = [mock_result_neg]
    await negotiation_service.confirm_delivery(db, neg_id, buyer_id)
    assert fake_neg.buyer_confirmed is True
    assert fake_neg.status == "accepted"  # Aún no completa

    # Segunda llamada → negociación + producto (para _record_gmv) + producto (para _record_transaction)
    fake_neg.buyer_confirmed = True  # simular estado previo guardado
    db.execute.side_effect = [mock_result_neg, mock_result_product, mock_result_product]
    await negotiation_service.confirm_delivery(db, neg_id, seller_id)
    assert fake_neg.seller_confirmed is True
    assert fake_neg.status == "delivered"


@pytest.mark.asyncio
async def test_confirm_delivery_invalid_status():
    """Lanza 400 si la negociación no está en estado 'accepted'."""
    db = AsyncMock()
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.status = "pending"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.confirm_delivery(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# Chat Messages
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_chat_message_logic():
    """Valida creación de mensajes y restricciones."""
    db = AsyncMock()
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()

    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.id = neg_id
    fake_neg.buyer_id = user_id
    fake_neg.seller_id = uuid.uuid4()
    fake_neg.status = "accepted"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    msg = await negotiation_service.create_chat_message(db, neg_id, user_id, "Test")
    assert msg.content == "Test"
    assert db.add.called

    # No es parte de la negociación
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_chat_message(db, neg_id, uuid.uuid4(), "Test")
    assert exc.value.status_code == 403

    # Negociación cerrada
    fake_neg.status = "delivered"
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_chat_message(db, neg_id, user_id, "Test")
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# Duplicate Negotiation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_negotiation_duplicate():
    """Lanza 409 si ya hay una negociación activa."""
    db = AsyncMock()
    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = MagicMock(
        spec=Product, seller_id=uuid.uuid4()
    )
    mock_result_existing = MagicMock()
    mock_result_existing.scalar_one_or_none.return_value = MagicMock(spec=Negotiation)

    db.execute.side_effect = [mock_result_product, mock_result_existing]

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_negotiation(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# Update Status
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_negotiation_status_logic():
    """Valida restricciones de cambio de estado."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MagicMock(
        spec=Negotiation, seller_id=seller_id, buyer_id=uuid.uuid4(), status="pending"
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    # Éxito
    await negotiation_service.update_negotiation_status(
        db, neg_id, seller_id, "accepted"
    )
    assert fake_neg.status == "accepted"

    # Prohibido (no es el vendedor)
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.update_negotiation_status(
            db, neg_id, uuid.uuid4(), "accepted"
        )
    assert exc.value.status_code == 403

    # Transición inválida (de accepted a pending)
    fake_neg.status = "accepted"
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.update_negotiation_status(
            db, neg_id, seller_id, "pending"
        )
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# Already Confirmed
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_confirm_delivery_already_confirmed():
    """Lanza 400 si el usuario ya confirmó anteriormente."""
    db = AsyncMock()
    user_id = uuid.uuid4()
    fake_neg = MagicMock(
        spec=Negotiation,
        buyer_id=user_id,
        status="accepted",
        buyer_confirmed=True,
        transaction_locked=True,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.confirm_delivery(db, uuid.uuid4(), user_id)
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# GMV Summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_gmv_summary_logic():
    """Valida cálculo de resumen GMV."""
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row.total_transactions = 10
    mock_row.total_gmv_cop = 50000.0

    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    db.execute.return_value = mock_result

    summary = await negotiation_service.get_gmv_summary(db)
    assert summary["total_transactions"] == 10
    assert summary["total_gmv_cop"] == 50000.0


# ---------------------------------------------------------------------------
# Deep Link generation
# ---------------------------------------------------------------------------


def test_generate_payment_deep_link_nequi():
    """Valida generación de deep link Nequi."""
    result = negotiation_service.generate_payment_deep_link(
        "nequi", "+573001234567", 15000
    )
    assert "nequi://" in result["deep_link_url"]
    assert "15000" in result["deep_link_url"]


def test_generate_payment_deep_link_daviplata():
    """Valida generación de deep link DaviPlata."""
    result = negotiation_service.generate_payment_deep_link("daviplata", "3009999999")
    assert "daviplata://" in result["deep_link_url"]
    assert result["amount_cop"] is None


def test_generate_payment_deep_link_invalid():
    """Lanza 400 para plataforma no soportada."""
    with pytest.raises(HTTPException) as exc:
        negotiation_service.generate_payment_deep_link("bancolombia", "3001234567")
    assert exc.value.status_code == 400
