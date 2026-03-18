"""PostgreSQL database setup using SQLAlchemy async engine.

Provides the async engine, session factory, and base model for all
ORM models. Connection is configured via DATABASE_URL in settings.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def create_engine():
    """Create the async SQLAlchemy engine from settings."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
    )


engine = None
async_session_factory = None


async def init_db():
    """Initialize database engine and create tables."""
    global engine, async_session_factory
    engine = create_engine()
    async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close the database engine."""
    global engine
    if engine:
        await engine.dispose()


async def get_db_session() -> AsyncSession:
    """Yield an async database session."""
    async with async_session_factory() as session:
        yield session