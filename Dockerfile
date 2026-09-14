# Base images are pinned to the exact versions that produced the D00 evidence.
# Digest pinning (image:tag@sha256:...) is added with the command in README
# "Image digests"; Dependabot's docker ecosystem then keeps them current.

# Stage 1: frontend assets (Tailwind build + vendored htmx/Alpine)
FROM oven/bun:1.4.2 AS assets
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY scripts ./scripts
COPY static/src ./static/src
COPY templates ./templates
COPY apps ./apps
RUN bun run build

# Stage 2: application image
FROM python:3.14.7-slim AS app
COPY --from=ghcr.io/astral-sh/uv:0.11.7 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# Dependencies first so code changes do not invalidate the layer.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .
COPY --from=assets /app/static/dist ./static/dist

# collectstatic needs importable prod settings but touches neither the
# database nor Redis; the placeholders never leave the build.
RUN SECRET_KEY=build-only \
    DATABASE_URL=postgresql://build:build@localhost:5432/build \
    REDIS_URL=redis://localhost:6379/0 \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

RUN useradd --create-home --uid 1000 app && chown -R app:app /app
USER app

EXPOSE 8080
CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips=*"]
