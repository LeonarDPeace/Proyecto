"""Modelo ORM — Product (productos del catálogo P2P).

Precios en COP (Peso Colombiano). CHECK constraint: price > 0.
Imágenes almacenadas como JSONB (lista de URLs).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    """Representa un producto publicado por un vendedor."""

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price > 0", name="ck_products_price_positive"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float] = mapped_column(
        Numeric(12, 2), nullable=False, comment="Precio en COP"
    )
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    image_urls: Mapped[list] = mapped_column(JSONB, server_default="'[]'::jsonb")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    seller: Mapped["User"] = relationship(back_populates="products")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Product {self.name} — ${self.price} COP>"
