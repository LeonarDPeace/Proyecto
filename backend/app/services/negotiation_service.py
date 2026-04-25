"""Service — Lógica de negocio para Negociaciones y Chat P2P.

HU 6.1: Chat interno en tiempo real.
HU 6.4: Marcado manual de "Transacción Completada" (ambas partes confirman).
HU 6.5: Registro automático del valor (GMV).
"""

import logging
import uuid
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat_message import ChatMessage
from app.models.gmv_metric import GmvMetric
from app.models.negotiation import Negotiation
from app.models.product import Product

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Negotiation CRUD
# ---------------------------------------------------------------------------


async def create_negotiation(
    db: AsyncSession,
    buyer_id: uuid.UUID,
    product_id: uuid.UUID,
    initial_message: str | None = None,
) -> Negotiation:
    """Crea una nueva negociación (comprador inicia contacto con vendedor).

    Valida que:
    - El producto exista y esté activo.
    - El comprador no sea el mismo vendedor (auto-compra).
    - No exista ya una negociación activa entre las mismas partes para el mismo producto.
    """
    # Obtener el producto
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.is_active == True,  # noqa: E712
            Product.is_deleted == False,  # noqa: E712
        )
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado o no disponible",
        )

    if product.seller_id == buyer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes negociar tu propio producto",
        )

    # Verificar negociación duplicada activa
    existing = await db.execute(
        select(Negotiation).where(
            Negotiation.buyer_id == buyer_id,
            Negotiation.product_id == product_id,
            Negotiation.status.in_(["pending", "accepted"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes una negociación activa para este producto",
        )

    negotiation = Negotiation(
        buyer_id=buyer_id,
        seller_id=product.seller_id,
        product_id=product_id,
        agreed_price_cop=float(product.price),
    )
    db.add(negotiation)
    await db.flush()

    # Si hay mensaje inicial, persistirlo como primer mensaje del chat
    if initial_message:
        message = ChatMessage(
            negotiation_id=negotiation.id,
            sender_id=buyer_id,
            content=initial_message,
        )
        db.add(message)
        await db.flush()

    return negotiation


async def get_negotiation_by_id(
    db: AsyncSession, negotiation_id: uuid.UUID
) -> Negotiation:
    """Busca una negociación por ID con mensajes cargados."""
    result = await db.execute(
        select(Negotiation)
        .options(selectinload(Negotiation.messages))
        .where(Negotiation.id == negotiation_id)
    )
    negotiation = result.scalar_one_or_none()
    if not negotiation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negociación no encontrada",
        )
    return negotiation


async def list_negotiations_by_user(
    db: AsyncSession, user_id: uuid.UUID
) -> Sequence[Negotiation]:
    """Lista todas las negociaciones de un usuario (como comprador o vendedor)."""
    result = await db.execute(
        select(Negotiation)
        .where(
            (Negotiation.buyer_id == user_id) | (Negotiation.seller_id == user_id)
        )
        .order_by(Negotiation.updated_at.desc())
    )
    return result.scalars().all()


async def update_negotiation_status(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    user_id: uuid.UUID,
    new_status: str,
) -> Negotiation:
    """Actualiza el estado de una negociación (solo el vendedor puede aceptar/rechazar)."""
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if negotiation.seller_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el vendedor puede aceptar o rechazar la negociación",
        )

    if negotiation.status not in ("pending",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cambiar de '{negotiation.status}' a '{new_status}'",
        )

    negotiation.status = new_status
    await db.flush()
    return negotiation


# ---------------------------------------------------------------------------
# HU 6.4: Confirmación de entrega (ambas partes)
# ---------------------------------------------------------------------------


async def confirm_delivery(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Negotiation:
    """Marca la confirmación de entrega de una de las partes.

    Cuando ambas partes confirman, el estado cambia a 'completed'
    y se registra automáticamente la métrica GMV (HU 6.5).
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if negotiation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede confirmar entrega en negociaciones aceptadas",
        )

    is_buyer = negotiation.buyer_id == user_id
    is_seller = negotiation.seller_id == user_id

    if not is_buyer and not is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    if is_buyer:
        if negotiation.buyer_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya confirmaste la entrega",
            )
        negotiation.buyer_confirmed = True

    if is_seller:
        if negotiation.seller_confirmed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya confirmaste la entrega",
            )
        negotiation.seller_confirmed = True

    # Si ambas partes confirmaron → completar transacción + registrar GMV
    if negotiation.buyer_confirmed and negotiation.seller_confirmed:
        negotiation.status = "completed"
        await _record_gmv(db, negotiation)

    await db.flush()
    return negotiation


# ---------------------------------------------------------------------------
# HU 6.5: Registro GMV
# ---------------------------------------------------------------------------


async def _record_gmv(db: AsyncSession, negotiation: Negotiation) -> None:
    """Registra el valor transaccional en la tabla de métricas GMV.

    Se ejecuta automáticamente cuando ambas partes confirman la entrega.
    """
    # Obtener el nombre del producto para snapshot
    result = await db.execute(
        select(Product).where(Product.id == negotiation.product_id)
    )
    product = result.scalar_one_or_none()
    product_name = product.name if product else None

    amount = negotiation.agreed_price_cop or (float(product.price) if product else 0.0)

    gmv = GmvMetric(
        negotiation_id=negotiation.id,
        product_id=negotiation.product_id,
        buyer_id=negotiation.buyer_id,
        seller_id=negotiation.seller_id,
        amount_cop=amount,
        product_name=product_name,
    )
    db.add(gmv)
    await db.flush()
    logger.info(
        "GMV registrado: negociación=%s, monto=%s COP",
        negotiation.id,
        amount,
    )


async def get_gmv_summary(db: AsyncSession) -> dict:
    """Calcula el resumen de GMV (total de transacciones y volumen)."""
    result = await db.execute(
        select(
            func.count(GmvMetric.id).label("total_transactions"),
            func.coalesce(func.sum(GmvMetric.amount_cop), 0).label("total_gmv_cop"),
        )
    )
    row = result.one()
    return {
        "total_transactions": row.total_transactions,
        "total_gmv_cop": float(row.total_gmv_cop),
        "period": "all_time",
    }


# ---------------------------------------------------------------------------
# Chat Messages (HU 6.1)
# ---------------------------------------------------------------------------


async def create_chat_message(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    sender_id: uuid.UUID,
    content: str,
) -> ChatMessage:
    """Crea y persiste un mensaje de chat dentro de una negociación.

    Valida que:
    - La negociación exista.
    - El remitente sea parte de la negociación (comprador o vendedor).
    - La negociación esté en estado 'pending' o 'accepted' (no completada/rechazada).
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if sender_id != negotiation.buyer_id and sender_id != negotiation.seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    if negotiation.status in ("completed", "rejected"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pueden enviar mensajes en negociaciones cerradas",
        )

    message = ChatMessage(
        negotiation_id=negotiation_id,
        sender_id=sender_id,
        content=content,
    )
    db.add(message)
    await db.flush()
    return message


async def list_chat_messages(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[ChatMessage]:
    """Lista los mensajes de una negociación con paginación.

    Solo permite el acceso a las partes de la negociación.
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if user_id != negotiation.buyer_id and user_id != negotiation.seller_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.negotiation_id == negotiation_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Deep Links — HU 6.2/6.3 (Nequi / DaviPlata)
# ---------------------------------------------------------------------------


def generate_payment_deep_link(
    platform: str,
    seller_phone: str,
    amount_cop: float | None = None,
) -> dict:
    """Genera un Deep Link URI para abrir la app de Nequi o DaviPlata.

    RESTRICCIÓN DE ARQUITECTURA: NO hay integración con APIs bancarias.
    Solo se genera un Deep Link / URI Scheme que intenta abrir la app
    en el dispositivo del usuario.
    """
    phone_clean = seller_phone.replace("+57", "").replace(" ", "").strip()

    if platform == "nequi":
        # Nequi Deep Link (URI scheme para Android/iOS)
        deep_link_url = f"nequi://payment?phoneNumber={phone_clean}"
        if amount_cop:
            deep_link_url += f"&amount={int(amount_cop)}"
    elif platform == "daviplata":
        # DaviPlata Deep Link
        deep_link_url = f"daviplata://send?phone={phone_clean}"
        if amount_cop:
            deep_link_url += f"&amount={int(amount_cop)}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Plataforma no soportada. Use 'nequi' o 'daviplata'",
        )

    return {
        "platform": platform,
        "deep_link_url": deep_link_url,
        "seller_phone": phone_clean,
        "amount_cop": amount_cop,
        "message": f"Enlace {platform.capitalize()} generado correctamente",
    }
