"""Esquemas Pydantic — Analytics (Sprint 5 — HU 8.7).

Dashboard financiero con rangos temporales variables.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    """Resumen financiero del vendedor para un período."""

    seller_id: uuid.UUID
    period: Literal["day", "week", "month", "semester", "all_time"]
    total_transactions: int
    total_revenue_cop: float
    total_discount_cop: float
    net_revenue_cop: float
    average_order_cop: float


class AnalyticsDataPoint(BaseModel):
    """Punto de datos para gráficos de línea temporal."""

    date: str
    revenue_cop: float
    transaction_count: int


class TransactionRead(BaseModel):
    """Lectura de una transacción individual."""

    id: uuid.UUID
    negotiation_id: uuid.UUID
    product_id: uuid.UUID | None
    buyer_id: uuid.UUID | None
    seller_id: uuid.UUID | None
    product_name: str | None
    quantity: int
    unit_price_cop: float
    subtotal_cop: float
    discount_cop: float
    total_cop: float
    payment_method: str | None
    coupon_code: str | None
    buyer_note: str | None
    completed_at: datetime

    model_config = {"from_attributes": True}
