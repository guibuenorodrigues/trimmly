from fastapi import FastAPI

from app.routers import urls
from app.routers.pages import create_homepage


def set_routes(app: FastAPI):
    # Pages routes
    app.include_router(create_homepage.router, prefix="/p", tags=["Pages"])

    # API Routes
    app.include_router(urls.router, tags=["API"])
