# Stub image (plan item 0.1): runs the app. The full multi-stage image comes in item 0.2 (spec §23.6).
FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src/ src/
RUN uv sync --frozen --no-dev

EXPOSE 8787
CMD ["reels-hub", "serve", "--host", "0.0.0.0", "--port", "8787"]
