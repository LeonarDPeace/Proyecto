"""Tests — Rating Service (HU 7.1 / 7.2).

Cobertura de:
- create_rating: éxito, negociación no encontrada, estado inválido, no participante, duplicado
- _update_user_reputation: recálculo de avg y total
- get_user_reputation: éxito, no encontrado
- list_ratings_for_user: listado
"""

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.negotiation import Negotiation
from app.models.rating import Rating
from app.services import rating_service


# ---------------------------------------------------------------------------
# create_rating — éxito
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rating_success():
    """Crea calificación exitosa en negociación delivered."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()
    seller_id = uuid.uuid4()
    neg_id = uuid.uuid4()

    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.id = neg_id
    fake_neg.buyer_id = buyer_id
    fake_neg.seller_id = seller_id
    fake_neg.status = "delivered"

    # 1. Negotiation found  2. No existing rating  3+4. _update_user_reputation
    mock_neg_result = MagicMock()
    mock_neg_result.scalar_one_or_none.return_value = fake_neg
    mock_no_existing = MagicMock()
    mock_no_existing.scalar_one_or_none.return_value = None

    mock_rep_row = MagicMock()
    mock_rep_row.total = 1
    mock_rep_row.avg = 4.5
    mock_rep_result = MagicMock()
    mock_rep_result.one.return_value = mock_rep_row
    mock_update_result = MagicMock()

    db.execute.side_effect = [
        mock_neg_result,    # negotiation
        mock_no_existing,   # duplicate check
        mock_rep_result,    # reputation select
        mock_update_result, # reputation update
    ]

    rating = await rating_service.create_rating(db, buyer_id, neg_id, 5, "Excelente")
    assert rating.reviewer_id == buyer_id
    assert rating.reviewed_id == seller_id
    assert rating.stars == 5
    assert db.add.called


# ---------------------------------------------------------------------------
# create_rating — negociación no encontrada
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rating_negotiation_not_found():
    """Lanza 404 si la negociación no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await rating_service.create_rating(db, uuid.uuid4(), uuid.uuid4(), 5)
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# create_rating — estado inválido
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rating_invalid_status():
    """Lanza 400 si la negociación no está en estado delivered."""
    db = AsyncMock()
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.status = "accepted"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await rating_service.create_rating(db, uuid.uuid4(), uuid.uuid4(), 4)
    assert exc.value.status_code == 400


# ---------------------------------------------------------------------------
# create_rating — no participante
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rating_not_participant():
    """Lanza 403 si el usuario no participa en la negociación."""
    db = AsyncMock()
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.buyer_id = uuid.uuid4()
    fake_neg.seller_id = uuid.uuid4()
    fake_neg.status = "delivered"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = fake_neg
    db.execute.return_value = mock_result

    outsider_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc:
        await rating_service.create_rating(db, outsider_id, uuid.uuid4(), 3)
    assert exc.value.status_code == 403


# ---------------------------------------------------------------------------
# create_rating — duplicado
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_rating_duplicate():
    """Lanza 409 si el usuario ya calificó la negociación."""
    db = AsyncMock()
    buyer_id = uuid.uuid4()
    fake_neg = MagicMock(spec=Negotiation)
    fake_neg.buyer_id = buyer_id
    fake_neg.seller_id = uuid.uuid4()
    fake_neg.status = "delivered"

    mock_neg = MagicMock()
    mock_neg.scalar_one_or_none.return_value = fake_neg
    mock_existing = MagicMock()
    mock_existing.scalar_one_or_none.return_value = MagicMock(spec=Rating)

    db.execute.side_effect = [mock_neg, mock_existing]

    with pytest.raises(HTTPException) as exc:
        await rating_service.create_rating(db, buyer_id, uuid.uuid4(), 5)
    assert exc.value.status_code == 409


# ---------------------------------------------------------------------------
# get_user_reputation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_user_reputation_success():
    """Retorna reputación consolidada."""
    db = AsyncMock()
    mock_row = MagicMock()
    mock_row.average_rating = 4.2
    mock_row.total_reviews = 8

    mock_result = MagicMock()
    mock_result.one_or_none.return_value = mock_row
    db.execute.return_value = mock_result

    rep = await rating_service.get_user_reputation(db, uuid.uuid4())
    assert rep["average_rating"] == 4.2
    assert rep["total_reviews"] == 8


@pytest.mark.asyncio
async def test_get_user_reputation_not_found():
    """Lanza 404 si el usuario no existe."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.one_or_none.return_value = None
    db.execute.return_value = mock_result

    with pytest.raises(HTTPException) as exc:
        await rating_service.get_user_reputation(db, uuid.uuid4())
    assert exc.value.status_code == 404


# ---------------------------------------------------------------------------
# list_ratings_for_user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_ratings_for_user():
    """Lista las calificaciones recibidas."""
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [MagicMock(spec=Rating)]
    db.execute.return_value = mock_result

    ratings = await rating_service.list_ratings_for_user(db, uuid.uuid4())
    assert len(ratings) == 1
