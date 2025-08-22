from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database.db import get_db
from app.services.url import URLService

DBSessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_url_service(db: DBSessionDep) -> URLService:  # type: ignore
    return URLService(db)
