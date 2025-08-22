from fastapi import FastAPI

from app.routers.urls import router

app = FastAPI(title="Trimmly")

app.include_router(router)
