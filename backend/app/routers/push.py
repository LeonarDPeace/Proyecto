"""Router — Push Notifications (HU 2.3)."""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()


class PushSubscription(BaseModel):
    """Schema para una suscripción Web Push que viene del Service Worker."""

    endpoint: str = Field(..., description="URL del servicio push (FCM, Autopush, etc)")
    keys: dict = Field(..., description="Claves de encriptación (p256dh, auth)")


@router.post("/subscribe", status_code=status.HTTP_200_OK)
async def subscribe_push(
    subscription: PushSubscription,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra o actualiza la suscripción del usuario a las notificaciones Push."""
    subs = list(current_user.push_subscriptions) if current_user.push_subscriptions else []

    # Evitar duplicados revisando si el endpoint ya existe.
    exists = any(s.get("endpoint") == subscription.endpoint for s in subs)

    if not exists:
        subs.append(subscription.model_dump())
        # Re-asignar para disparar la detección de cambio de SQLAlchemy en JSONB.
        current_user.push_subscriptions = subs
        await db.commit()

    return {"message": "Suscripción guardada correctamente"}
