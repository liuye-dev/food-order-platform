FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev --no-install-project

COPY backend /app/backend

WORKDIR /app/backend

RUN chmod +x /app/backend/docker-entrypoint.sh

EXPOSE 8000

CMD ["/app/backend/docker-entrypoint.sh"]
