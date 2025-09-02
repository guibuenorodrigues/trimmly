from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=5,
    pool_recycle=3600,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FASTAPI exclusive:
    An async dependency to provide a database session.
    It automatically handles closing the session.
    """

    async with AsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    A standalone context manager for use outside of FastAPI's Depends.
    Ensures the session is properly closed.
    """
    session = AsyncSession(engine)
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
