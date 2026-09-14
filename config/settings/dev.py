# config/settings/dev.py

import os

from .base import *  # noqa: F403
from .base import REDIS_OPTIONS, database_from_url

DEBUG = True
SECRET_KEY = "dev-only-not-a-secret"  # noqa: S105
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": database_from_url(
        os.environ.get(
            "DATABASE_URL",
            "postgresql://hookrelay:hookrelay@127.0.0.1:55433/hookrelay",
        )
    )
}

REDIS_URL = os.environ.get(
    "REDIS_URL",
    "redis://127.0.0.1:56380/0",
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": REDIS_OPTIONS,
    }
}
