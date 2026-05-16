"""Tests — Report Service (HU 7.3).

Cobertura de:
- create_report: producto válido, duplicado, auto-reporte, sin target
- _check_auto_hide: umbral de auto-ocultamiento
- review_report: transiciones reviewed/dismissed/inválido
- list_pending_reports, get_product_report_summary
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.models.product import Product
from app.models.report import AUTO_HIDE_THRESHOLD, Report
from app.services import report_service


# ---------------------------------------------------------------------------
# create_report — éxito con producto
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_for_product_success():
    """Crea un reporte sobre un producto existente."""
    db = AsyncMock()
    reporter_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    product_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.id = product_id
    fake_product.seller_id = seller_id
    fake_product.is_deleted = False

    # 1. Producto encontrado  2. Sin reporte duplicado
    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = fake_product
    mock_result_existing = MagicMock()
    mock_result_existing.scalar_one_or_none.return_value = None

    # 3. _check_auto_hide → count < threshold
    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = 1

    db.execute.side_effect = [mock_result_product, mock_result_existing, mock_result_count]

    report = await report_service.create_report(
        db, reporter_id, "spam", product_id=product_id, description="Contenido repetido"
    )
    assert report.reporter_id == reporter_id
    assert report.reason == "spam"
    assert db.add.called


# ---------------------------------------------------------------------------
# create_report — auto-reporte bloqueado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_self_report_blocked():
    """No permite que un usuario se reporte a sí mismo."""
    db = AsyncMock()
    user_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = user_id  # Mismo usuario
    fake_product.is_deleted = False

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_product
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await report_service.create_report(db, user_id, "fraud", product_id=uuid.uuid4())
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# create_report — sin target (ni producto ni usuario)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_no_target():
    """Lanza 400 si no se proporciona ni producto ni usuario."""
    db = AsyncMock()

    with pytest.raises(HTTPException) as exc:
        await report_service.create_report(db, uuid.uuid4(), "offensive")
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# create_report — duplicado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_duplicate_blocked():
    """Lanza 409 si el usuario ya reportó el mismo producto."""
    db = AsyncMock()
    reporter_id = uuid.uuid4()

    fake_product = MagicMock(spec=Product)
    fake_product.seller_id = uuid.uuid4()
    fake_product.is_deleted = False

    mock_result_product = MagicMock()
    mock_result_product.scalar_one_or_none.return_value = fake_product
    mock_result_existing = MagicMock()
    mock_result_existing.scalar_one_or_none.return_value = MagicMock(spec=Report)

    db.execute.side_effect = [mock_result_product, mock_result_existing]

    with pytest.raises(HTTPException) as exc:
        await report_service.create_report(db, reporter_id, "spam", product_id=uuid.uuid4())
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# create_report — producto no encontrado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_report_product_not_found():
    """Lanza 404 si el producto no existe."""
    db = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await report_service.create_report(db, uuid.uuid4(), "fraud", product_id=uuid.uuid4())
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# _check_auto_hide — umbral alcanzado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_check_auto_hide_triggers():
    """Oculta producto cuando se alcanza el umbral de reportes."""
    db = AsyncMock()
    product_id = uuid.uuid4()

    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = AUTO_HIDE_THRESHOLD  # Exactamente el umbral

    mock_result_update = MagicMock()

    db.execute.side_effect = [mock_result_count, mock_result_update]

    await report_service._check_auto_hide(db, product_id)
    assert db.execute.call_count == 2  # count + update
    assert db.flush.called


# ---------------------------------------------------------------------------
# review_report — éxito y estados inválidos
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_review_report_success():
    """Actualiza estado de un reporte a 'reviewed'."""
    db = AsyncMock()
    fake_report = MagicMock(spec=Report)
    fake_report.status = "pending"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_report
    db.execute.return_value = mock_result

    result = await report_service.review_report(db, uuid.uuid4(), "reviewed")
    assert result.status == "reviewed"


@pytest.mark.asyncio
async def test_review_report_not_found():
    """Lanza 404 si el reporte no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await report_service.review_report(db, uuid.uuid4(), "reviewed")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_review_report_invalid_status():
    """Lanza 400 si el nuevo estado es inválido."""
    db = AsyncMock()
    fake_report = MagicMock(spec=Report)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_report
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await report_service.review_report(db, uuid.uuid4(), "aprobado")
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# get_product_report_summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_product_report_summary():
    """Valida estructura del resumen de reportes."""
    db = AsyncMock()
    product_id = uuid.uuid4()

    # Total count
    mock_total = MagicMock()
    mock_total.scalar.return_value = 5
    # Reason breakdown
    mock_reason = MagicMock()
    mock_reason.all.return_value = [("spam", 3), ("fraud", 2)]
    # Product active status
    mock_product = MagicMock()
    mock_product.one_or_none.return_value = MagicMock(is_active=False)

    db.execute.side_effect = [mock_total, mock_reason, mock_product]

    result = await report_service.get_product_report_summary(db, product_id)
    assert result["total_reports"] == 5
    assert result["is_auto_hidden"] is True
    assert result["reports_by_reason"]["spam"] == 3


# ---------------------------------------------------------------------------
# list_pending_reports
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_pending_reports():
    """Devuelve lista de reportes pendientes."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock(spec=Report)]
    db.execute.return_value = mock_result

    result = await report_service.list_pending_reports(db)
    assert len(result) == 1

