"""Service — Lógica de negocio para Negociaciones y Chat P2P.

HU 6.1: Chat interno en tiempo real.
HU 6.4: Marcado manual de "Transacción Completada" (ambas partes confirman).
HU 6.5: Registro automático del valor (GMV).
HU 8.1: Máquina de estados de pedido.
HU 8.3: Parámetros extra (cantidad, nota).
HU 8.5: Bloqueo transaccional.
HU 8.2: Notificaciones transaccionales por correo.
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
from app.models.transaction import Transaction

logger = logging.getLogger(__name__)

# --- HU 8.1: Máquina de estados válida ---
VALID_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"accepted", "rejected", "cancelled"},
    "accepted": {"paused", "rejected", "cancelled", "delivered"},
    "paused": {"accepted", "cancelled"},
    "rejected": set(),
    "cancelled": set(),
    "delivered": set(),
}


# ---------------------------------------------------------------------------
# Negotiation CRUD
# ---------------------------------------------------------------------------


async def create_negotiation(
    db: AsyncSession,
    buyer_id: uuid.UUID,
    product_id: uuid.UUID,
    initial_message: str | None = None,
    quantity: int = 1,
    buyer_note: str | None = None,
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
        quantity=quantity,
        buyer_note=buyer_note,
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
        .where((Negotiation.buyer_id == user_id) | (Negotiation.seller_id == user_id))
        .order_by(Negotiation.updated_at.desc())
    )
    return result.scalars().all()


async def update_negotiation_status(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    user_id: uuid.UUID,
    new_status: str,
) -> Negotiation:
    """Actualiza el estado de una negociación según la máquina de estados (HU 8.1).

    Transiciones válidas:
    - pending  → accepted, rejected, cancelled
    - accepted → paused, rejected, cancelled, delivered
    - paused   → accepted, cancelled
    - rejected / cancelled / delivered → (terminal, sin transiciones)
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    # Validar que el usuario es parte de la negociación
    is_seller = negotiation.seller_id == user_id
    is_buyer = negotiation.buyer_id == user_id
    if not is_seller and not is_buyer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No eres parte de esta negociación",
        )

    # Solo vendedor puede aceptar/rechazar/pausar; comprador puede cancelar
    seller_actions = {"accepted", "rejected", "paused"}
    if new_status in seller_actions and not is_seller:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el vendedor puede aceptar, rechazar o pausar",
        )

    # Validar transición válida
    allowed = VALID_TRANSITIONS.get(negotiation.status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición inválida: '{negotiation.status}' → '{new_status}'",
        )

    negotiation.status = new_status
    await db.flush()

    # HU 8.2: Notificación por email al cambiar estado
    await _notify_status_change(db, negotiation, new_status)

    return negotiation


async def _notify_status_change(
    db: AsyncSession, negotiation: Negotiation, new_status: str
) -> None:
    """Envía notificación por email ante cambios de estado (HU 8.2)."""
    try:
        from app.services.auth_service import get_user_by_id

        buyer = await get_user_by_id(db, negotiation.buyer_id)
        seller = await get_user_by_id(db, negotiation.seller_id)
        if not buyer or not seller:
            return

        status_labels = {
            "accepted": "Pedido Aceptado ✅",
            "paused": "Pedido Pausado ⏸️",
            "rejected": "Pedido Rechazado ❌",
            "cancelled": "Pedido Cancelado 🚫",
            "delivered": "Pedido Entregado 📦",
        }
        label = status_labels.get(new_status, new_status)

        from app.services.email_service import send_transactional_email

        # Notificar al comprador
        await send_transactional_email(
            email=buyer.email,
            subject=f"VeraMarket — {label}",
            body=f"Tu pedido ha cambiado a estado: {label}.",
        )
        # Notificar al vendedor (si la acción fue del comprador)
        await send_transactional_email(
            email=seller.email,
            subject=f"VeraMarket — {label}",
            body=f"Un pedido ha cambiado a estado: {label}.",
        )
    except Exception:
        logger.warning("No se pudo enviar notificación de estado")


# ---------------------------------------------------------------------------
# HU 8.5: Establecer método de pago (bloqueo transaccional)
# ---------------------------------------------------------------------------


async def set_payment_method(
    db: AsyncSession,
    negotiation_id: uuid.UUID,
    user_id: uuid.UUID,
    payment_method: str,
    coupon_code: str | None = None,
) -> Negotiation:
    """Registra el método de pago y bloquea la transacción.

    Solo el comprador puede establecer el método de pago.
    La transacción queda bloqueada (transaction_locked=True) para
    impedir el cierre sin método de pago (HU 8.5).
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if negotiation.buyer_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el comprador puede establecer el método de pago",
        )

    if negotiation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El método de pago solo se puede establecer en negociaciones aceptadas",
        )

    negotiation.payment_method = payment_method
    negotiation.coupon_code = coupon_code
    negotiation.transaction_locked = True

    # Validar cupón si existe
    if coupon_code:
        from app.services.coupon_service import validate_coupon

        validation = await validate_coupon(
            db, coupon_code, negotiation.seller_id,
            float(negotiation.agreed_price_cop or 0) * negotiation.quantity,
        )
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation["message"],
            )

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

    Cuando ambas partes confirman, el estado cambia a 'delivered'
    y se registra automáticamente la métrica GMV (HU 6.5)
    y la transacción detallada (HU 8.7).

    HU 8.5: Requiere que transaction_locked=True (método de pago registrado).
    """
    negotiation = await get_negotiation_by_id(db, negotiation_id)

    if negotiation.status != "accepted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede confirmar entrega en negociaciones aceptadas",
        )

    # HU 8.5: Bloqueo transaccional
    if not negotiation.transaction_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes seleccionar un método de pago antes de confirmar la entrega",
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

    # Si ambas partes confirmaron → completar transacción + registrar GMV + Transaction
    if negotiation.buyer_confirmed and negotiation.seller_confirmed:
        negotiation.status = "delivered"
        await _record_gmv(db, negotiation)
        await _record_transaction(db, negotiation)
        await _notify_status_change(db, negotiation, "delivered")

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


async def _record_transaction(db: AsyncSession, negotiation: Negotiation) -> None:
    """Registra el detalle de la transacción para analítica (HU 8.7)."""
    result = await db.execute(
        select(Product).where(Product.id == negotiation.product_id)
    )
    product = result.scalar_one_or_none()
    product_name = product.name if product else None

    unit_price = float(negotiation.agreed_price_cop or (product.price if product else 0))
    quantity = negotiation.quantity or 1
    subtotal = round(unit_price * quantity, 2)

    # Calcular descuento si hay cupón
    discount = 0.0
    if negotiation.coupon_code:
        from app.services.coupon_service import redeem_coupon, validate_coupon

        validation = await validate_coupon(
            db, negotiation.coupon_code, negotiation.seller_id, subtotal
        )
        if validation["valid"]:
            discount = validation["discount_amount"]
            await redeem_coupon(db, negotiation.coupon_code)

    total = round(subtotal - discount, 2)

    tx = Transaction(
        negotiation_id=negotiation.id,
        product_id=negotiation.product_id,
        buyer_id=negotiation.buyer_id,
        seller_id=negotiation.seller_id,
        product_name=product_name,
        quantity=quantity,
        unit_price_cop=unit_price,
        subtotal_cop=subtotal,
        discount_cop=discount,
        total_cop=total,
        payment_method=negotiation.payment_method,
        coupon_code=negotiation.coupon_code,
        buyer_note=negotiation.buyer_note,
    )
    db.add(tx)
    await db.flush()
    logger.info("Transacción registrada: %s, total=%s COP", tx.id, total)


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

    if negotiation.status in ("delivered", "rejected", "cancelled"):
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
