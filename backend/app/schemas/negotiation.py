"""Esquemas Pydantic — Negotiation & Chat (Sprint 4/5).

HU 6.1: Chat en tiempo real.
HU 6.2/6.3: Deep Links Nequi/DaviPlata.
HU 6.4: Marcado manual de transacción completada.
HU 6.5: Registro GMV.
HU 8.1: Máquina de estados de pedido.
HU 8.3: Parámetros extra (cantidad, nota).
HU 8.5: Bloqueo transaccional.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Negotiation
# ---------------------------------------------------------------------------


class NegotiationCreate(BaseModel):
    """Datos para iniciar una negociación (comprador → vendedor)."""

    product_id: uuid.UUID
    initial_message: str | None = Field(
        default=None,
        max_length=1000,
        description="Mensaje opcional al iniciar la negociación",
    )
    quantity: int = Field(
        default=1,
        ge=1,
        description="Cantidad del producto solicitada",
    )
    buyer_note: str | None = Field(
        default=None,
        max_length=500,
        description="Nota personalizada del comprador",
    )


class NegotiationRead(BaseModel):
    """Datos de lectura de una negociación."""

    id: uuid.UUID
    buyer_id: uuid.UUID
    seller_id: uuid.UUID
    product_id: uuid.UUID
    status: str
    buyer_confirmed: bool
    seller_confirmed: bool
    agreed_price_cop: float | None
    quantity: int
    buyer_note: str | None
    payment_method: str | None
    coupon_code: str | None
    transaction_locked: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NegotiationStatusUpdate(BaseModel):
    """Actualización del estado de una negociación."""

    status: Literal["accepted", "paused", "rejected", "cancelled"]


class SetPaymentMethod(BaseModel):
    """Establecer método de pago (HU 8.5) — bloquea la transacción."""

    payment_method: Literal["efectivo", "nequi", "daviplata"]
    coupon_code: str | None = Field(
        default=None,
        max_length=30,
        description="Código de cupón opcional",
    )


class NegotiationConfirmDelivery(BaseModel):
    """Confirmación de entrega — puede ser del comprador o vendedor."""

    pass  # No body required; user identity from JWT determines the role.


# ---------------------------------------------------------------------------
# Chat Messages
# ---------------------------------------------------------------------------


class ChatMessageCreate(BaseModel):
    """Datos para enviar un mensaje en el chat."""

    content: str = Field(..., min_length=1, max_length=2000)


class ChatMessageRead(BaseModel):
    """Datos de lectura de un mensaje de chat."""

    id: uuid.UUID
    negotiation_id: uuid.UUID
    sender_id: uuid.UUID
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Deep Links — HU 6.2/6.3 (Nequi / DaviPlata)
# ---------------------------------------------------------------------------


class PaymentDeepLink(BaseModel):
    """Genera un Deep Link para Nequi o DaviPlata."""

    platform: Literal["nequi", "daviplata"]
    deep_link_url: str
    seller_phone: str
    amount_cop: float | None = None
    message: str = "Enlace generado correctamente"


# ---------------------------------------------------------------------------
# GMV — HU 6.5
# ---------------------------------------------------------------------------


class GmvMetricRead(BaseModel):
    """Lectura de una métrica GMV individual."""

    id: uuid.UUID
    negotiation_id: uuid.UUID
    product_id: uuid.UUID | None
    buyer_id: uuid.UUID | None
    seller_id: uuid.UUID | None
    amount_cop: float
    product_name: str | None
    completed_at: datetime

    model_config = {"from_attributes": True}


class GmvSummary(BaseModel):
    """Resumen agregado de GMV."""

    total_transactions: int
    total_gmv_cop: float
    period: str = "all_time"
