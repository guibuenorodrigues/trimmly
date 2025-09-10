FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UV_PROJECT_ENVIRONMENT=/usr/local
ENV PYTHONPATH=/code

COPY uv.lock pyproject.toml ./

RUN uv sync --locked --refresh

COPY ./app /code/app

COPY alembic.ini /code/
COPY ./migration /code/migration

EXPOSE 8090

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8090", "--proxy-headers", "--forwarded-allow-ips", "*"]
