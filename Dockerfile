# Four stages; only `runtime` ships. Every external input is an immutable
# index digest measured and scanned by the owner (docs/LEVERANS-D00.md, v1.5.2);
# tests/security/test_image_references.py refuses tag-only references.
#
# Builder and runtime are the proven-compatible Chainguard pair: the venv is
# created in latest-dev against /usr/bin/python and copied into latest, whose
# interpreter layout matches (verified by import in the owner's local proof).
# The runtime has no shell, no package manager, no uv, no Bun, no compiler.

ARG PYTHON_BUILDER_IMAGE=cgr.dev/chainguard/python:latest-dev@sha256:7d75104053e1b1b9e3316743e52acc3113be6750918fa7b1c2600fed8b590547
ARG PYTHON_RUNTIME_IMAGE=cgr.dev/chainguard/python:latest@sha256:459a10eaf994a3244330e6c514375c9064f14a34729fe75746f35d1f9fc5a149
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6
ARG BUN_IMAGE=oven/bun:1.4.2@sha256:9114c058aeae42162ee16dd5084b95fe9473970bb6bcb5b232ab1630f0546895

# ---- Stage 1: uv binary source ------------------------------------------
FROM ${UV_IMAGE} AS uv

# ---- Stage 2: frontend assets -------------------------------------------
FROM ${BUN_IMAGE} AS assets
WORKDIR /src
COPY package.json bun.lock tsconfig.json ./
RUN bun install --frozen-lockfile
COPY scripts ./scripts
COPY static/src ./static/src
COPY templates ./templates
COPY apps ./apps
RUN bun run typecheck:tools && bun run build

# ---- Stage 3: Python dependency builder ---------------------------------
FROM ${PYTHON_BUILDER_IMAGE} AS builder
USER root
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
ENV UV_PYTHON=/usr/bin/python \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_CACHE=1
COPY pyproject.toml uv.lock ./
RUN /usr/local/bin/uv sync --locked --no-dev --no-install-project
COPY manage.py ./
COPY config ./config
COPY apps ./apps
COPY templates ./templates
COPY --from=assets /src/static/dist ./static/dist
# collectstatic needs importable production settings and touches neither the
# database nor Redis; the placeholders never leave this stage.
RUN SECRET_KEY=build-only \
    DATABASE_URL=postgresql://build:build@localhost:5432/build \
    REDIS_URL=redis://localhost:6379/0 \
    ALLOWED_HOSTS=localhost \
    DJANGO_SETTINGS_MODULE=config.settings.prod \
    /app/.venv/bin/python manage.py collectstatic --noinput

# ---- Stage 4: minimal runtime -------------------------------------------
FROM ${PYTHON_RUNTIME_IMAGE} AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod
WORKDIR /app
COPY --from=builder --chown=65532:65532 /app/.venv ./.venv
COPY --from=builder --chown=65532:65532 /app/manage.py ./manage.py
COPY --from=builder --chown=65532:65532 /app/config ./config
COPY --from=builder --chown=65532:65532 /app/apps ./apps
COPY --from=builder --chown=65532:65532 /app/templates ./templates
COPY --from=builder --chown=65532:65532 /app/static/dist ./static/dist
COPY --from=builder --chown=65532:65532 /app/staticfiles ./staticfiles
USER 65532
EXPOSE 8080
# The base image sets ENTRYPOINT ["/usr/bin/python"]; cleared so CMD is the
# whole command. Forwarded-header trust comes from FORWARDED_ALLOW_IPS in the
# environment (uvicorn's own variable; default 127.0.0.1). No wildcard.
ENTRYPOINT []
CMD ["/app/.venv/bin/uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
