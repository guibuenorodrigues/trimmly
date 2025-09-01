import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, responses, status
from fastapi.responses import HTMLResponse

from app.config import settings
from app.routers.urls import URLServiceDep

router = APIRouter()


@router.get("/create", response_class=HTMLResponse)
async def shortener_page(request: Request):
    error_message = request.session.get("error_message")

    if "error_message" in request.session:
        del request.session["error_message"]

    context = {"request": request}
    if error_message:
        context["error_message"] = error_message

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
        return responses.RedirectResponse(url=f"/p/404?error={e}")


@router.get("/create/shortened", response_class=HTMLResponse)
async def shortened_page(url_service: URLServiceDep, request: Request):
    last_key_id = request.session.get("last_key_id")
    print(last_key_id)

    if "last_key_id" in request.session:
        del request.session["last_key_id"]

    if last_key_id is None:
        request.session["error_message"] = "Invalid request without a valid session. Please try again."
        return responses.RedirectResponse(url="/p/create")

    data = await url_service.get_one_by_id(id=uuid.UUID(last_key_id))
    if not data:
        request.session["error_message"] = "Invalid request. No shortened key available. Please try again."
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
