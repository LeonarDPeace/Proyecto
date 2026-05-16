"""Tests — Ratings (HU 7.1/7.2).

Verifica la creación de calificaciones y la reputación consolidada.
"""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.main import app
from app.models.rating import Rating
from app.models.user import User


def _mock_user(user_id: uuid.UUID | None = None) -> User:
    u = MagicMock(spec=User)
    u.id = user_id or uuid.uuid4()
    u.role = "comprador"
    return u


async def override_get_db():
    yield AsyncMock()


@pytest.mark.asyncio
async def test_create_rating():
    """POST /api/v1/ratings/ crea una calificación."""
    user_id = uuid.uuid4()
    neg_id = uuid.uuid4()
    fake_rating = MagicMock(spec=Rating)
    fake_rating.id = uuid.uuid4()
    fake_rating.negotiation_id = neg_id
    fake_rating.reviewer_id = user_id
    fake_rating.reviewed_id = uuid.uuid4()
    fake_rating.stars = 5
    fake_rating.comment = "Excelente!"
    fake_rating.created_at = datetime.now(UTC)

    app.dependency_overrides[get_current_user] = lambda: _mock_user(user_id)
    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.ratings.rating_service.create_rating", new_callable=AsyncMock
    ) as mock_create:
        mock_create.return_value = fake_rating
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/ratings/",
                json={
                    "negotiation_id": str(neg_id),
                    "stars": 5,
                    "comment": "Excelente!",
                },
            )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["stars"] == 5


@pytest.mark.asyncio
async def test_get_user_reputation():
    """GET /api/v1/ratings/user/{user_id}/reputation obtiene la reputación."""
    user_id = uuid.uuid4()

    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.ratings.rating_service.get_user_reputation", new_callable=AsyncMock
    ) as mock_get:
        mock_get.return_value = {
            "user_id": user_id,
            "average_rating": 4.5,
            "total_reviews": 10,
        }
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/ratings/user/{user_id}/reputation")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["average_rating"] == 4.5


@pytest.mark.asyncio
async def test_list_user_ratings():
    """GET /api/v1/ratings/user/{user_id} lista las calificaciones."""
    user_id = uuid.uuid4()
    fake_rating = MagicMock(spec=Rating)
    fake_rating.id = uuid.uuid4()
    fake_rating.negotiation_id = uuid.uuid4()
    fake_rating.reviewer_id = uuid.uuid4()
    fake_rating.reviewed_id = user_id
    fake_rating.stars = 4
    fake_rating.comment = "Bueno"
    fake_rating.created_at = datetime.now(UTC)

    app.dependency_overrides[get_db] = override_get_db

    with patch(
        "app.routers.ratings.rating_service.list_ratings_for_user",
        new_callable=AsyncMock,
    ) as mock_list:
        mock_list.return_value = [fake_rating]
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/v1/ratings/user/{user_id}")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["stars"] == 4
