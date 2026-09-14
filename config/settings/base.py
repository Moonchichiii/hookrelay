"""Settings shared by every environment. dev/test/prod override, never duplicate."""

import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, unquote, urlsplit

from django.utils.csp import CSP

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def database_from_url(url: str) -> dict[str, Any]:
    # Fly and Neon hand out a single DATABASE_URL; parsing it here avoids a
    # dependency for five lines of stdlib. Query parameters (sslmode,
    # channel_binding, ...) pass straight through to libpq as OPTIONS.
    parts = urlsplit(url)
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parts.path.lstrip("/"),
        "USER": unquote(parts.username or ""),
        "PASSWORD": unquote(parts.password or ""),
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or ""),
        # connect_timeout bounds /readyz when the database is unreachable and
        # is applied last so a URL parameter cannot override it.
        "OPTIONS": {**dict(parse_qsl(parts.query)), "connect_timeout": 3},
    }


SECRET_KEY = os.environ.get("SECRET_KEY", "")
DEBUG = False
ALLOWED_HOSTS: list[str] = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "django_htmx",
    "django_tasks_db",
    "apps.accounts",
]

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.csp.ContentSecurityPolicyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": database_from_url(os.environ.get("DATABASE_URL", ""))}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REDIS_URL = os.environ.get("REDIS_URL", "")
# Socket timeouts bound /readyz when Redis is unreachable; they pass through
# RedisCache to redis-py's connection pool.
REDIS_OPTIONS = {"socket_connect_timeout": 2, "socket_timeout": 2}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": REDIS_OPTIONS,
    }
}

# The task queue lives in the same PostgreSQL as the domain rows. django-tasks-db
# enqueues with a plain ORM insert, so an enqueue inside transaction.atomic()
# commits or rolls back together with the rows that caused it (verified against
# 0.13.0 source; there is no enqueue-on-commit option to get wrong).
TASKS = {
    "default": {
        "BACKEND": "django_tasks_db.DatabaseBackend",
        "OPTIONS": {"id_function": "uuid.uuid7"},
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static" / "dist"]
STATIC_ROOT = BASE_DIR / "staticfiles"

REST_FRAMEWORK = {
    # Deny by default; every endpoint opts in to its own authentication and
    # permission classes explicitly.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Hookrelay API",
    "DESCRIPTION": "Webhook delivery: publish events, manage endpoints, inspect deliveries.",
    "VERSION": "0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# Strict self-only policy. Local htmx, the Alpine CSP build and built Tailwind
# CSS need no inline code; a nonce is added only when something proves it must.
SECURE_CSP = {
    "default-src": [CSP.SELF],
    "script-src": [CSP.SELF],
    "style-src": [CSP.SELF],
    "connect-src": [CSP.SELF],
    "img-src": [CSP.SELF, "data:"],
    "font-src": [CSP.SELF],
    "object-src": [CSP.NONE],
    "base-uri": [CSP.SELF],
    "frame-ancestors": [CSP.NONE],
    "form-action": [CSP.SELF],
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"stdout": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["stdout"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}
