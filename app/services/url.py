from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.exceptions import DuplicateEntityError, EntityNotFoundError
from app.logger import logger
from app.models.url import URLMapping
from app.schemas.url import ExpandedURLResponse, ShortenedURLResponse
from app.services.kgs import get_next_key, validate_custom_key


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

        new_url_mapping = URLMapping(original_url=long_url, short_key=short_key)
        await self.save_new_url(new_url_mapping)

        return ShortenedURLResponse(id=new_url_mapping.id, short_key=short_key)

    async def update_on_click(self, url_mapping: URLMapping) -> None:
        """
        Update the click count and last clicked timestamp for a shortened URL.
        """
        try:
            url_mapping.clicks_count += 1
            url_mapping.last_clicked_at = datetime.now(timezone.utc)

            await self.db.commit()
            await self.db.refresh(url_mapping)
        except Exception as e:
            await self.db.rollback()
            logger.warning(f"unable to update click {url_mapping.short_key}: {e}")

    async def get_one(self, short_key: str) -> URLMapping | None:
        """
        Retrieve a URL mapping by its short key.
        Raises EntityNotFoundException if no URL mapping is found.
        """
        stmt = select(URLMapping).where(URLMapping.short_key == short_key)
        url = (await self.db.exec(stmt)).one_or_none()
        return url

    async def expand_url(self, short_key: str) -> ExpandedURLResponse:
        """
        Expand a shortened URL and update metrics.
        Raises EntityNotFoundException if short_key is not found.
        """
        url_mapping = await self.get_one(short_key)

        if not url_mapping:
            raise EntityNotFoundError("URLMapping", short_key)

        await self.update_on_click(url_mapping)

        return ExpandedURLResponse(
            id=url_mapping.id,
            short_key=short_key,
            long_url=url_mapping.original_url,
            clicks_count=url_mapping.clicks_count,
            last_clicked_at=url_mapping.last_clicked_at,
            created_at=url_mapping.created_at,
            updated_at=url_mapping.updated_at,
        )
