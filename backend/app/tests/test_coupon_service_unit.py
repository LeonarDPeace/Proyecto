"""Tests — Coupon Service (HU 8.9).

Cobertura de:
- create_coupon: éxito (global y con productos), duplicado
- validate_coupon: cupón válido, inválido, expirado, restricción de producto
- redeem_coupon: incremento de current_uses
- update_coupon: actualización parcial, no encontrado
- delete_coupon: éxito, no encontrado
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.coupon import Coupon
from app.models.product import Product
from app.services import coupon_service


# ---------------------------------------------------------------------------
# create_coupon — éxito
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_coupon_success():
    """Crea un cupón global (sin productos específicos)."""
    db = AsyncMock()
    seller_id = uuid.uuid4()

    # No existe cupón con ese código
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    coupon = await coupon_service.create_coupon(
        db,
        seller_id=seller_id,
        code="BIENVENIDA10",
        discount_percent=10.0,
        max_uses=50,
    )
    assert coupon.code == "BIENVENIDA10"
    assert coupon.discount_percent == 10.0
    assert db.add.called


@pytest.mark.asyncio
async def test_create_coupon_with_products():
    """Crea un cupón con productos específicos (M2M) — verifica query de productos."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    product_ids = [uuid.uuid4(), uuid.uuid4()]

    # Check de duplicado
    mock_no_existing = MagicMock()
    mock_no_existing.scalar_one_or_none.return_value = None

    # Productos del vendedor — retornar lista vacía para evitar
    # asignar MagicMock a relación ORM (causa _sa_instance_state error)
    mock_products = MagicMock()
    mock_products.scalars.return_value.all.return_value = []

    db.execute.side_effect = [mock_no_existing, mock_products]

    coupon = await coupon_service.create_coupon(
        db,
        seller_id=seller_id,
        code="PROMO2X1",
        discount_fixed_cop=2000.0,
        applicable_product_ids=product_ids,
    )
    assert coupon.code == "PROMO2X1"
    assert db.execute.call_count == 2  # duplicate check + product fetch


# ---------------------------------------------------------------------------
# create_coupon — duplicado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_coupon_duplicate():
    """Lanza 409 si el código ya existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = MagicMock(spec=Coupon)
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await coupon_service.create_coupon(db, uuid.uuid4(), "DUPLICADO")
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# validate_coupon — válido
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_coupon_valid():
    """Valida cupón activo con descuento porcentual."""
    db = AsyncMock()

    fake_coupon = MagicMock(spec=Coupon)
    fake_coupon.code = "DESCUENTO20"
    fake_coupon.is_valid.return_value = True
    fake_coupon.applicable_products = []  # Global
    fake_coupon.calculate_discount.return_value = 4000.0

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    result = await coupon_service.validate_coupon(db, "DESCUENTO20", uuid.uuid4(), 20000.0)
    assert result["valid"] is True
    assert result["discount_amount"] == 4000.0


# ---------------------------------------------------------------------------
# validate_coupon — no encontrado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_coupon_not_found():
    """Retorna valid=False si el cupón no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    result = await coupon_service.validate_coupon(db, "INVALIDO", uuid.uuid4(), 10000.0)
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# validate_coupon — expirado/agotado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_coupon_expired():
    """Retorna valid=False si el cupón está expirado o agotado."""
    db = AsyncMock()
    fake_coupon = MagicMock(spec=Coupon)
    fake_coupon.is_valid.return_value = False
    fake_coupon.applicable_products = []

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    result = await coupon_service.validate_coupon(db, "EXPIRADO", uuid.uuid4(), 10000.0)
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# validate_coupon — restricción de producto
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_coupon_wrong_product():
    """Retorna valid=False si el cupón no aplica para el producto."""
    db = AsyncMock()
    allowed_product_id = uuid.uuid4()
    wrong_product_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.id = allowed_product_id

    fake_coupon = MagicMock(spec=Coupon)
    fake_coupon.is_valid.return_value = True
    fake_coupon.applicable_products = [fake_product]

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    result = await coupon_service.validate_coupon(
        db, "RESTRINGIDO", uuid.uuid4(), 10000.0, product_id=wrong_product_id
    )
    assert result["valid"] is False


# ---------------------------------------------------------------------------
# redeem_coupon
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_redeem_coupon_increments_uses():
    """Incrementa current_uses al redimir."""
    db = AsyncMock()
    fake_coupon = MagicMock(spec=Coupon)
    fake_coupon.current_uses = 0

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    await coupon_service.redeem_coupon(db, "PROMO")
    assert fake_coupon.current_uses == 1


# ---------------------------------------------------------------------------
# update_coupon
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_coupon_success():
    """Actualiza campos parciales de un cupón."""
    db = AsyncMock()
    seller_id = uuid.uuid4()
    fake_coupon = MagicMock(spec=Coupon)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    result = await coupon_service.update_coupon(
        db, uuid.uuid4(), seller_id, is_active=False, max_uses=100
    )
    assert result.is_active is False
    assert result.max_uses == 100


@pytest.mark.asyncio
async def test_update_coupon_not_found():
    """Lanza 404 si el cupón no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await coupon_service.update_coupon(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# delete_coupon
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_coupon_success():
    """Elimina un cupón existente."""
    db = AsyncMock()
    fake_coupon = MagicMock(spec=Coupon)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_coupon
    db.execute.return_value = mock_result

    await coupon_service.delete_coupon(db, uuid.uuid4(), uuid.uuid4())
    assert db.delete.called


@pytest.mark.asyncio
async def test_delete_coupon_not_found():
    """Lanza 404 si el cupón no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await coupon_service.delete_coupon(db, uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404
