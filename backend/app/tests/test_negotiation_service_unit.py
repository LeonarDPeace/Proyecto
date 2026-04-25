"""Tests — Negotiation Service logic (HU 6.1-6.5).

Asegura cobertura > 90% en app/services/negotiation_service.py.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.negotiation import Negotiation
from app.models.product import Product
from app.services import negotiation_service


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

    # Mock DB results
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


@pytest.mark.asyncio
async def test_confirm_delivery_logic_flow():
    """Valida flujo de confirmación dual y cierre."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()

    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.id = neg_id
    fake_neg.buyer_id = buyer_id
    fake_neg.seller_id = seller_id
    fake_neg.status = "accepted"
    fake_neg.buyer_confirmed = False
    fake_neg.seller_confirmed = False
    fake_neg.product_id = uuid.uuid4()
    fake_neg.agreed_price_cop = 5000.0

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    # Confirmación Comprador
    await negotiation_service.confirm_delivery(db, neg_id, buyer_id)
    assert fake_neg.buyer_confirmed is True
    assert fake_neg.status == "accepted" # Aún no completa

    # Confirmación Vendedor
    fake_neg.buyer_confirmed = True # Simular estado previo
    await negotiation_service.confirm_delivery(db, neg_id, seller_id)
    assert fake_neg.seller_confirmed is True
    assert fake_neg.status == "completed"


@pytest.mark.asyncio
async def test_confirm_delivery_invalid_status():
    """Lanza 400 si la negociación no está aceptada."""
    db = AsyncMock()
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.status = "pending"
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.confirm_delivery(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 400


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

    # Caso: No es parte de la negociación
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_chat_message(db, neg_id, uuid.uuid4(), "Test")
    assert exc.value.status_code == 403

    # Caso: Negociación cerrada
    fake_neg.status = "completed"
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_chat_message(db, neg_id, user_id, "Test")
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_create_negotiation_duplicate():
    """Lanza 409 si ya hay una negociación activa."""
    db = AsyncMock()
    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = MagicMock(spec=Product, seller_id=uuid.uuid4())
    
    mock_result_existing = MagicMock()
    mock_result_existing.scalar_one_or_none.return_value = MagicMock(spec=Negotiation)
    
    db.execute.side_effect = [mock_result_product, mock_result_existing]

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.create_negotiation(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_negotiation_status_logic():
    """Valida restricciones de cambio de estado."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_neg = MagicMock(spec=Negotiation, seller_id=seller_id, status="pending")
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    # Success
    await negotiation_service.update_negotiation_status(db, neg_id, seller_id, "accepted")
    assert fake_neg.status == "accepted"

    # Forbidden (not seller)
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.update_negotiation_status(db, neg_id, uuid.uuid4(), "accepted")
    assert exc.value.status_code == 403

    # Invalid transition (already accepted)
    fake_neg.status = "accepted"
    with pytest.raises(HTTPException) as exc:
        await negotiation_service.update_negotiation_status(db, neg_id, seller_id, "rejected")
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_confirm_delivery_already_confirmed():
    """Lanza 400 si ya se confirmó."""
    db = AsyncMock()
    user_id = uuid.uuid4()
    fake_neg = MagicMock(spec=Negotiation, buyer_id=user_id, status="accepted", buyer_confirmed=True)
    
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await negotiation_service.confirm_delivery(db, uuid.uuid4(), user_id)
    assert exc.value.status_code == 400


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
