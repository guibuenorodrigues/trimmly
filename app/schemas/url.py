import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.url import URLMapping


class ShortenURLRequest(BaseModel):
    long_url: str
    short_key: str | None = None


class ShortenedURLResponse(BaseModel):
    id: uuid.UUID
    short_key: str


class ExpandedURLResponse(BaseModel):
    id: uuid.UUID
    short_key: str
    long_url: str
    clicks_count: int
    last_clicked_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_url_mapping(cls, url_mapping: URLMapping) -> "ExpandedURLResponse":
        return cls(
            id=url_mapping.id,
            short_key=url_mapping.short_key,
            long_url=url_mapping.original_url,
            clicks_count=url_mapping.clicks_count,
            last_clicked_at=url_mapping.last_clicked_at,
            created_at=url_mapping.created_at,
            updated_at=url_mapping.updated_at,
        )
