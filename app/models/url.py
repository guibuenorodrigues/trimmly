import uuid
from datetime import datetime

from sqlmodel import DateTime, Field

from app.models.base import BaseSQLModel


class URLMappingBase(BaseSQLModel):
    __tablename__ = "url_mapping"

    short_key: str = Field(index=True, unique=True, max_length=8, nullable=False)
    original_url: str = Field(max_length=2048, nullable=False)
    clicks_count: int = Field(default=0)
    last_clicked_at: datetime | None = Field(
        default=None,
        nullable=True,
        sa_type=DateTime(timezone=True),
    )


class URLMappingCreate(URLMappingBase):
    pass


class URLMappingUpdate(BaseSQLModel):
    short_key: str | None = Field(default=None, max_length=8)
    original_url: str | None = Field(default=None, max_length=2048)
    clicks_count: int | None = Field(default=None)
    last_clicked_at: datetime | None = Field(default=None)


class URLMapping(URLMappingBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
