"""VeraMarket — Conexión asíncrona a PostgreSQL con SQLAlchemy 2.0."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Clase base declarativa para todos los modelos ORM."""

    pass


async def get_db() -> AsyncSession:  # type: ignore[misc]
    """Dependency — genera una sesión de base de datos por request.

    Yields:
        AsyncSession: Sesión activa de SQLAlchemy.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
