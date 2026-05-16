"""Tests — Analytics Service (HU 8.7).

Cobertura de:
- get_seller_summary: con y sin filtro de periodo
- get_seller_timeline: generación de puntos de datos diarios
- get_seller_transactions: listado con y sin filtro
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import analytics_service


@pytest.mark.asyncio
async def test_get_seller_summary_all_time():
    """Resumen financiero sin filtro temporal."""
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row.total_transactions = 15
    mock_row.gross_revenue = 250000.0
    mock_row.net_revenue = 230000.0
    mock_row.total_discount = 20000.0
    mock_row.avg_order = 15333.33

    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    db.execute.return_value = mock_result

    summary = await analytics_service.get_seller_summary(db, uuid.uuid4(), "all_time")
    assert summary["total_transactions"] == 15
    assert summary["total_revenue_cop"] == 250000.0
    assert summary["net_revenue_cop"] == 230000.0
    assert summary["period"] == "all_time"


@pytest.mark.asyncio
async def test_get_seller_summary_with_period():
    """Resumen financiero con filtro de periodo (week)."""
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row.total_transactions = 3
    mock_row.gross_revenue = 45000.0
    mock_row.net_revenue = 45000.0
    mock_row.total_discount = 0.0
    mock_row.avg_order = 15000.0

    mock_result = MagicMock()
    mock_result.one.return_value = mock_row
    db.execute.return_value = mock_result

    summary = await analytics_service.get_seller_summary(db, uuid.uuid4(), "week")
    assert summary["total_transactions"] == 3
    assert summary["period"] == "week"


@pytest.mark.asyncio
async def test_get_seller_timeline():
    """Genera puntos de datos de timeline."""
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row.day = datetime(2026, 5, 10, tzinfo=UTC)
    mock_row.revenue = 50000.0
    mock_row.count = 5

    mock_result = MagicMock()
    mock_result.all.return_value = [mock_row]
    db.execute.return_value = mock_result

    timeline = await analytics_service.get_seller_timeline(db, uuid.uuid4(), "month")
    assert len(timeline) == 1
    assert timeline[0]["date"] == "2026-05-10"
    assert timeline[0]["revenue_cop"] == 50000.0
    assert timeline[0]["transaction_count"] == 5


@pytest.mark.asyncio
async def test_get_seller_timeline_all_time():
    """Timeline con period=all_time usa delta de 365 días."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.all.return_value = []
    db.execute.return_value = mock_result

    timeline = await analytics_service.get_seller_timeline(db, uuid.uuid4(), "all_time")
    assert timeline == []


@pytest.mark.asyncio
async def test_get_seller_transactions():
    """Lista transacciones con filtro temporal."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    txs = await analytics_service.get_seller_transactions(db, uuid.uuid4(), "month")
    assert txs == []


@pytest.mark.asyncio
async def test_get_seller_transactions_all_time():
    """Lista transacciones sin filtro temporal."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    db.execute.return_value = mock_result

    txs = await analytics_service.get_seller_transactions(db, uuid.uuid4(), "all_time")
    assert txs == []
