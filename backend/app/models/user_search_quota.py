"""Modelo ORM — UserSearchQuota (control de consumo NLU diario por usuario)."""

import uuid
from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserSearchQuota(Base):
    """Registro diario de búsquedas inteligentes por usuario."""

    __tablename__ = "user_search_quotas"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "search_date", name="uq_user_search_quota_user_day"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    search_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    searches_used: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    daily_limit: Mapped[int] = mapped_column(
        Integer, server_default="10", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    user: Mapped["User"] = relationship(back_populates="search_quotas")  # noqa: F821

    def __repr__(self) -> str:
        return f"<UserSearchQuota user={self.user_id} day={self.search_date} used={self.searches_used}>"
