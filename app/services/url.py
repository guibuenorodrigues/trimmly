from datetime import datetime, timezone

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.url import URLMapping
from app.schemas.url import ExpandedURLResponse, ShortenedURLResponse
from app.services.kgs import generate_key, validate_custom_key


class URLService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_new_url(self, url_mapping: URLMapping) -> ShortenedURLResponse:
        """
        Save a new shortened URL.
        """
        self.db.add(url_mapping)
        await self.db.commit()
        await self.db.refresh(url_mapping)
        return ShortenedURLResponse(id=url_mapping.id, short_key=url_mapping.short_key)

    async def shorten_url(self, long_url: str, short_key: str = "") -> ShortenedURLResponse:
        """
        Shorten a long URL.
        """

        if not short_key:
            # Generate a new short key if not provided
            short_key = generate_key()
        else:
            # Validate the provided short key
            is_valid, error_message = validate_custom_key(short_key)
            if not is_valid:
                raise ValueError(f"Invalid custom short key: {error_message}")

        new_url_mapping = URLMapping(long_url=long_url, short_key=short_key)
        await self.save_new_url(new_url_mapping)

        return ShortenedURLResponse(id=new_url_mapping.id, short_key=short_key)

    async def update_on_click(self, url_mapping: URLMapping) -> None:
        """
        Update the click count and last clicked timestamp for a shortened URL.
        """

        url_mapping.clicks_count += 1
        url_mapping.last_clicked_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(url_mapping)

    async def expand_url(self, short_key: str) -> ExpandedURLResponse:
        """
        Expand a shortened URL.
        """
        url_mapping = await self.db.get(URLMapping, short_key=short_key)
        if not url_mapping:
            raise ValueError("Shortened URL not found")

        await self.update_on_click(url_mapping)

        # Implementation goes here
        return ExpandedURLResponse(
            id=url_mapping.id,
            short_key=short_key,
            long_url=url_mapping.long_url,
            clicks_count=url_mapping.clicks_count,
            last_clicked_at=url_mapping.last_clicked_at,
            created_at=url_mapping.created_at,
            updated_at=url_mapping.updated_at,
        )
