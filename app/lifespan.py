from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.services.kgs import fill_key_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    fill_key_pool(pool_size=settings.KGS_KEY_POOL_SIZE)

    yield
