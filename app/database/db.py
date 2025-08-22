from collections.abc import AsyncGenerator

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
    An async dependency to provide a database session.
    It automatically handles closing the session.
    """

    async with AsyncSession(engine) as session:
        yield session
