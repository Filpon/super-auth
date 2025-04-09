FROM python:3.12.7

COPY --from=ghcr.io/astral-sh/uv:0.5.2 /uv /uvx /bin/

WORKDIR /app

COPY . /app


RUN uv sync --frozen --no-cache

CMD ["./.venv/bin/alembic" "upgrade", "head"]

CMD [".venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]