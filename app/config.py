from functools import lru_cache

from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    DEBUG: bool = False
    ENABLE_FILE_LOGGING: bool = True
    KGS_KEY_POOL_SIZE: int = 100
    TEMPLATE: Jinja2Templates = Jinja2Templates(directory="app/templates")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
