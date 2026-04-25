"""Modelo ORM — ChatMessage (mensajes en tiempo real del chat P2P).

HU 6.1: Chat interno en tiempo real.
Los mensajes se persisten en la base de datos para historial de auditoría.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ChatMessage(Base):
    """Representa un mensaje individual dentro de una negociación/chat."""

    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    negotiation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("negotiations.id", ondelete="CASCADE"), nullable=False
    )
    sender_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    negotiation: Mapped["Negotiation"] = relationship(  # noqa: F821
        back_populates="messages"
    )
    sender: Mapped["User"] = relationship()  # noqa: F821

    def __repr__(self) -> str:
        return f"<ChatMessage {self.id} — negotiation={self.negotiation_id}>"
