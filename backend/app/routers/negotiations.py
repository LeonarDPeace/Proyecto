"""Router — Negotiations (Negociación P2P, Chat y Deep Links).

Sprint 4 — EP-06: Negociación y Cierre P2P (Frictionless).
HU 6.1: Chat interno en tiempo real.
HU 6.2/6.3: Deep Links para Nequi / DaviPlata.
HU 6.4: Marcado manual de "Transacción Completada".
HU 6.5: Registro automático del valor (GMV).
"""

import logging
import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.negotiation import (
    ChatMessageCreate,
    ChatMessageRead,
    GmvSummary,
    NegotiationCreate,
    NegotiationRead,
    NegotiationStatusUpdate,
    PaymentDeepLink,
)
from app.services import negotiation_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# Negotiations CRUD
# ---------------------------------------------------------------------------


@router.post(
    "/",
    response_model=NegotiationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_negotiation(
    data: NegotiationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationRead:
    """Inicia una nueva negociación (comprador contacta al vendedor)."""
    negotiation = await negotiation_service.create_negotiation(
        db,
        buyer_id=current_user.id,
        product_id=data.product_id,
        initial_message=data.initial_message,
    )
    await db.commit()
    await db.refresh(negotiation)
    return negotiation


@router.get("/", response_model=list[NegotiationRead])
async def list_my_negotiations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[NegotiationRead]:
    """Lista todas las negociaciones del usuario autenticado."""
    return await negotiation_service.list_negotiations_by_user(db, current_user.id)


@router.get("/{negotiation_id}", response_model=NegotiationRead)
async def get_negotiation(
    negotiation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationRead:
    """Obtiene el detalle de una negociación."""
    negotiation = await negotiation_service.get_negotiation_by_id(db, negotiation_id)

    if current_user.id not in (negotiation.buyer_id, negotiation.seller_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    return negotiation


@router.patch("/{negotiation_id}/status", response_model=NegotiationRead)
async def update_status(
    negotiation_id: uuid.UUID,
    data: NegotiationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationRead:
    """Actualiza el estado de una negociación (aceptar/rechazar — solo vendedor)."""
    negotiation = await negotiation_service.update_negotiation_status(
        db, negotiation_id, current_user.id, data.status
    )
    await db.commit()
    await db.refresh(negotiation)
    return negotiation


# ---------------------------------------------------------------------------
# HU 6.4: Confirmación de entrega
# ---------------------------------------------------------------------------


@router.patch("/{negotiation_id}/confirm", response_model=NegotiationRead)
async def confirm_delivery(
    negotiation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NegotiationRead:
    """Confirma la entrega de la transacción (comprador o vendedor).

    Cuando ambas partes confirman, el estado cambia a 'completed'
    y se registra el valor transaccional (GMV) automáticamente.
    """
    negotiation = await negotiation_service.confirm_delivery(
        db, negotiation_id, current_user.id
    )
    await db.commit()
    await db.refresh(negotiation)
    return negotiation


# ---------------------------------------------------------------------------
# HU 6.1: Chat Messages
# ---------------------------------------------------------------------------


@router.get("/{negotiation_id}/messages", response_model=list[ChatMessageRead])
async def list_messages(
    negotiation_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Sequence[ChatMessageRead]:
    """Lista los mensajes del chat de una negociación."""
    return await negotiation_service.list_chat_messages(
        db, negotiation_id, current_user.id, limit=limit, offset=offset
    )


@router.post(
    "/{negotiation_id}/messages",
    response_model=ChatMessageRead,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    negotiation_id: uuid.UUID,
    data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChatMessageRead:
    """Envía un mensaje en el chat de una negociación."""
    message = await negotiation_service.create_chat_message(
        db, negotiation_id, current_user.id, data.content
    )
    await db.commit()
    await db.refresh(message)

    # --- Notificar vía WebSocket (Modo Híbrido) ---
    try:
        from app.routers.websockets import manager
        await manager.broadcast_to_room(
            str(negotiation_id),
            {
                "type": "message",
                "id": str(message.id),
                "negotiation_id": str(negotiation_id),
                "sender_id": str(current_user.id),
                "sender_name": current_user.name,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
            }
        )
    except Exception:
        logger.warning("No se pudo notificar mensaje vía WS (fallback a REST exitoso)")

    return message


# ---------------------------------------------------------------------------
# HU 6.2/6.3: Deep Links (Nequi / DaviPlata)
# ---------------------------------------------------------------------------


@router.get("/{negotiation_id}/payment-link", response_model=PaymentDeepLink)
async def get_payment_deep_link(
    negotiation_id: uuid.UUID,
    platform: str = Query(
        ..., pattern="^(nequi|daviplata)$", description="nequi o daviplata"
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaymentDeepLink:
    """Genera un Deep Link para abrir Nequi o DaviPlata con los datos del vendedor.

    RESTRICCIÓN: NO hay integración con APIs bancarias.
    Solo genera un URI Scheme para intentar abrir la app en el dispositivo.
    """
    negotiation = await negotiation_service.get_negotiation_by_id(db, negotiation_id)

    if current_user.id not in (negotiation.buyer_id, negotiation.seller_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    if negotiation.status not in ("accepted",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El enlace de pago solo está disponible en negociaciones aceptadas",
        )

    # Obtener el teléfono del vendedor (si lo tiene habilitado)
    from app.services.auth_service import get_user_by_id

    seller = await get_user_by_id(db, negotiation.seller_id)
    if not seller or not seller.phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El vendedor no ha registrado su número de teléfono",
        )

    return negotiation_service.generate_payment_deep_link(
        platform=platform,
        seller_phone=seller.phone,
        amount_cop=negotiation.agreed_price_cop,
    )


# ---------------------------------------------------------------------------
# HU 6.5: GMV Summary
# ---------------------------------------------------------------------------


@router.get("/metrics/gmv", response_model=GmvSummary)
async def get_gmv_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GmvSummary:
    """Obtiene el resumen de volumen bruto de mercancía (GMV)."""
    return await negotiation_service.get_gmv_summary(db)
