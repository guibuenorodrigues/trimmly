from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.config import settings

router = APIRouter()


@router.get("/create", response_class=HTMLResponse)
async def home_page(request: Request):
    print("ettete")
    context = {"request": request}
    return settings.TEMPLATE.TemplateResponse(name="shortened.html", context=context)
