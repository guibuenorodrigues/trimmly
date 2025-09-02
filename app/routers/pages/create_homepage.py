import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, responses, status
from fastapi.responses import HTMLResponse

from app.config import settings
from app.flash_message import flash_message, get_flashed_messages
from app.routers.urls import URLServiceDep

router = APIRouter()


@router.get("/create", response_class=HTMLResponse)
async def shortener_page(request: Request):
    context = {"request": request, "messages": get_flashed_messages(request)}
    return settings.TEMPLATE.TemplateResponse(name="shortener.html", context=context)


async def get_create_form_data(
    long_url: Annotated[str, Form()],
    short_key: Annotated[str, Form()],
    expire_date: Annotated[str, Form()],
):
    return {"long_url": long_url, "short_key": short_key, "expire_date": expire_date}


@router.post("/create/generate")
async def shortner_url(
    request: Request,
    form: Annotated[dict, Depends(get_create_form_data)],
    url_service: URLServiceDep,
):
    try:
        shortened_url = await url_service.shorten_url(form["long_url"], form["short_key"])

        request.session["last_key_id"] = str(shortened_url.id)

        return responses.RedirectResponse(
            url="/p/create/shortened",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as e:
        flash_message(request, f"Error to shortener your url. {e}", "error")
        return responses.RedirectResponse(url="/p/create", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/create/shortened", response_class=HTMLResponse)
async def shortened_page(url_service: URLServiceDep, request: Request):
    last_key_id = request.session.get("last_key_id")

    if "last_key_id" in request.session:
        del request.session["last_key_id"]

    if last_key_id is None:
        flash_message(request, "Invalid url key. Please try again.", "error")
        return responses.RedirectResponse(url="/p/create")

    data = await url_service.get_one_by_id(id=uuid.UUID(last_key_id))
    if not data:
        flash_message(request, "There is no valid shortened url. Please try again.", "error")
        return responses.RedirectResponse(url="/p/create")

    context = {
        "request": request,
        "shortened_url": f"{settings.BASE_URL}/u/{data.short_key}",
        "original_url": data.original_url,
    }
    return settings.TEMPLATE.TemplateResponse(
        name="shortened.html",
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
        context=context,
    )
