import uuid
from datetime import datetime

from pydantic import BaseModel


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
