import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import cache
from app.database.db import get_db_session
from app.exceptions import DuplicateEntityError, EntityNotFoundError
from app.logger import logger
from app.models.url import URLMapping
from app.schemas.url import ExpandedURLResponse, ShortenedURLResponse
from app.services.kgs import get_next_key, validate_custom_key
from app.utils import smart_url_schema_detection


class URLService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_new_url(self, url_mapping: URLMapping) -> ShortenedURLResponse:
        """
        Save a new shortened URL.
        Raises DuplicateEntityException if short_key already exists.
        """
        try:
            self.db.add(url_mapping)
            await self.db.commit()
            await self.db.refresh(url_mapping)
            return ShortenedURLResponse(id=url_mapping.id, short_key=url_mapping.short_key)
        except IntegrityError as e:
            await self.db.rollback()
            # Check if it's a unique constraint violation on short_key
            if "short_key" in str(e.orig):
                raise DuplicateEntityError("URLMapping", "short_key", url_mapping.short_key) from e
            # Re-raise the original error if it's not the expected duplicate
            raise

    async def shorten_url(self, long_url: str, short_key: str = "") -> ShortenedURLResponse:
        """
        Shorten a long URL.
        """

        if not short_key:
            # Generate a new short key if not provided
            short_key = get_next_key()
        else:
            # Validate the provided short key
            is_valid, error_message = validate_custom_key(short_key)
            if not is_valid:
                raise ValueError(f"Invalid custom short key: {error_message}")

        schemed_long_url = smart_url_schema_detection(long_url)
        new_url_mapping = URLMapping(original_url=schemed_long_url, short_key=short_key)
        await self.save_new_url(new_url_mapping)

        cache.set_url_value(short_key, new_url_mapping)

        return ShortenedURLResponse(id=new_url_mapping.id, short_key=short_key)

    async def update_click_metrics(self, short_key: str) -> None:
        """
        Update click metrics for a given short key.
        """
        async with get_db_session() as db:
            try:
                stmt = select(URLMapping).where(URLMapping.short_key == short_key)
                url_mapping = await db.scalar(stmt)

                if not url_mapping:
                    raise EntityNotFoundError("URLMapping", short_key)

                url_mapping.clicks_count += 1
                url_mapping.last_clicked_at = datetime.now(timezone.utc)
                await db.commit()
                await db.refresh(url_mapping)
                logger.info(f"Updated click metrics for short_key: {short_key}")
            except Exception as e:
                await db.rollback()
                logger.warning(f"unable to update click {short_key}: {e}")

    async def get_one(self, short_key: str) -> URLMapping | None:
        """
        Retrieve a URL mapping by its short key.
        Raises EntityNotFoundException if no URL mapping is found.
        """
        stmt = select(URLMapping).where(URLMapping.short_key == short_key)
        url = (await self.db.exec(stmt)).one_or_none()
        return url

    async def get_one_by_id(self, id: uuid.UUID) -> URLMapping | None:
        """
        Retrieve a URL mapping by its id.
        Raises EntityNotFoundException if no URL mapping is found.
        """
        stmt = select(URLMapping).where(URLMapping.id == id)
        url = (await self.db.exec(stmt)).one_or_none()
        return url

    async def expand_url(self, short_key: str) -> ExpandedURLResponse:
        """
        Expand a shortened URL and update metrics.
        Raises EntityNotFoundException if short_key is not found.
        """
        cached_url = cache.get_url_value(short_key)

        if cached_url:
            logger.info(f"Cache hit for short_key: {short_key}")
            return ExpandedURLResponse.from_url_mapping(cached_url)

        url_mapping = await self.get_one(short_key)

        if not url_mapping:
            raise EntityNotFoundError("URLMapping", short_key)

        return ExpandedURLResponse.from_url_mapping(url_mapping)
