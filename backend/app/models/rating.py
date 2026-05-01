"""Modelo ORM — Rating (calificación de transacciones).

Sprint 5 — EP-07: Moderación y Reputación Comunitaria.
HU 7.1: Calificación de transacciones (1 a 5 estrellas).

Solo se habilita la calificación después de que la transacción
se marque como completada (HU 6.4).
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Rating(Base):
    """Calificación de 1 a 5 estrellas tras una transacción completada."""

    __tablename__ = "ratings"
    __table_args__ = (
        CheckConstraint("stars >= 1 AND stars <= 5", name="ck_ratings_stars_range"),
        UniqueConstraint(
            "negotiation_id",
            "reviewer_id",
            name="uq_ratings_one_review_per_user",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    negotiation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("negotiations.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que deja la calificación",
    )
    reviewed_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Usuario que recibe la calificación",
    )
    stars: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Calificación de 1 a 5 estrellas",
    )
    comment: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Comentario opcional de la calificación",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    reviewer: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[reviewer_id],
    )
    reviewed: Mapped["User"] = relationship(  # noqa: F821
        foreign_keys=[reviewed_id],
    )
    negotiation: Mapped["Negotiation"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<Rating {self.id} — {self.stars}★ by {self.reviewer_id}>"
