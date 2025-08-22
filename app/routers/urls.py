from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_url_service
from app.schemas.url import ShortenURLRequest, ShortenedURLResponse
from app.services.url import URLService

router = APIRouter(prefix="")

URLServiceDep = Annotated[URLService, Depends(get_url_service)]


@router.post("/url")
async def create_url(payload: ShortenURLRequest, url_service: URLServiceDep) -> ShortenedURLResponse:
    short_url = await url_service.shorten_url(payload.long_url, payload.short_key)
    if not short_url:
        raise HTTPException(status_code=400, detail="URL shortening failed")

    return ShortenedURLResponse.model_validate(short_url)
