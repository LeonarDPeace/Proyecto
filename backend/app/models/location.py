"""Modelo ORM — Location (ubicación geoespacial de vendedores en el campus).

Usa PostGIS (GEOMETRY Point, SRID 4326) para geolocalización.
Coordenadas por defecto: UAO, Cali (3.3516, -76.5320).
"""

import uuid
from datetime import UTC, datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Location(Base):
    """Ubicación geoespacial de un vendedor dentro del campus."""

    __tablename__ = "locations"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default="uuid_generate_v4()",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    campus: Mapped[str] = mapped_column(String(100), nullable=False, server_default="'UAO'")
    coordinates = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    label: Mapped[str | None] = mapped_column(String(200), nullable=True, comment="Ej: Cafetería Central, Sinapsis")

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="location")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Location {self.label or self.campus}>"
