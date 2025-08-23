from typing import Annotated

from fastapi import APIRouter, Depends, responses, status

from app.dependencies import get_url_service
from app.exceptions import EntityNotFoundError
from app.schemas.url import ShortenURLRequest, ShortenedURLResponse
from app.services.url import URLService

router = APIRouter(prefix="")

URLServiceDep = Annotated[URLService, Depends(get_url_service)]


@router.post("/url")
async def create_url(payload: ShortenURLRequest, url_service: URLServiceDep) -> ShortenedURLResponse:
    short_url = await url_service.shorten_url(payload.long_url, payload.short_key)
    return ShortenedURLResponse.model_validate(short_url)


@router.get("/{short_key}")
async def expand_url(short_key: str, url_service: URLServiceDep) -> None:
    try:
        original_url = await url_service.expand_url(short_key)
        return responses.RedirectResponse(
            url=original_url.long_url,
            status_code=status.HTTP_308_PERMANENT_REDIRECT,
            headers={"X-Original-URL": original_url.long_url, "Cache-Control": "no-store"},
        )
    except EntityNotFoundError:
        return responses.RedirectResponse(url="url/404", status_code=status.HTTP_404_NOT_FOUND)
