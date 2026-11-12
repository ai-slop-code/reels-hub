# Multi-stage image, linux/arm64 only (spec §23.6, R63). Stages: node (HyperFrames, pinned, R126),
# runtime (the image the run machine pulls), test (runtime + dev tools + tests; never shipped).
# INSECURE_TLS=1 is set only by scripts/container-test.sh on the build machine (R125). It is a
# build argument used inside RUN steps; it never reaches an ENV or a file in the final image.

FROM node:22-bookworm-slim AS node
ARG INSECURE_TLS=0
WORKDIR /opt/hyperframes
COPY package.json package-lock.json ./
RUN if [ "$INSECURE_TLS" = 1 ]; then npm config set strict-ssl false; fi \
 && PUPPETEER_SKIP_DOWNLOAD=1 npm ci --omit=dev --no-audit --no-fund

FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df AS runtime
ARG INSECURE_TLS=0
ARG VERSION=0.0.0
ARG REVISION=unknown
LABEL org.opencontainers.image.title="Reels Hub" \
      org.opencontainers.image.source="https://github.com/ai-slop-code/reels-hub" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${REVISION}"

RUN if [ "$INSECURE_TLS" = 1 ]; then \
      printf 'Acquire::https::Verify-Peer "false";\nAcquire::https::Verify-Host "false";\n' \
        > /etc/apt/apt.conf.d/99insecure-build; \
    fi \
 && apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg chromium fonts-noto-core \
 && rm -rf /var/lib/apt/lists/* /etc/apt/apt.conf.d/99insecure-build

COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /opt/hyperframes /opt/hyperframes
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    REELS_HUB_GIT_SHA=$REVISION \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium \
    PATH=/app/.venv/bin:/opt/hyperframes/node_modules/.bin:$PATH

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    flags=""; \
    if [ "$INSECURE_TLS" = 1 ]; then flags="--allow-insecure-host pypi.org --allow-insecure-host files.pythonhosted.org"; fi; \
    uv sync --frozen --no-dev --no-install-project $flags
COPY src/ src/
COPY bin/ bin/
RUN --mount=type=cache,target=/root/.cache/uv \
    flags=""; \
    if [ "$INSECURE_TLS" = 1 ]; then flags="--allow-insecure-host pypi.org --allow-insecure-host files.pythonhosted.org"; fi; \
    uv sync --frozen --no-dev $flags

EXPOSE 8787
CMD ["reels-hub", "serve", "--host", "0.0.0.0", "--port", "8787"]

FROM runtime AS test
ARG INSECURE_TLS=0
COPY tests/ tests/
RUN --mount=type=cache,target=/root/.cache/uv \
    flags=""; \
    if [ "$INSECURE_TLS" = 1 ]; then flags="--allow-insecure-host pypi.org --allow-insecure-host files.pythonhosted.org"; fi; \
    uv sync --frozen $flags
CMD ["pytest", "-m", "container"]
