import os

from .base import *  # noqa: F403
from .base import REDIS_OPTIONS, database_from_url

SECRET_KEY = "test-only-not-a-secret"  # noqa: S105
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# Redis db 1 keeps test cache.clear() separate from the dev cache.
DATABASES = {
    "default": database_from_url(
        os.environ.get("DATABASE_URL", "postgresql://hookrelay:hookrelay@127.0.0.1:55433/hookrelay")
    )
}
REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:56380/1")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": REDIS_OPTIONS,
    }
}

TASKS = {"default": {"BACKEND": "django.tasks.backends.immediate.ImmediateBackend"}}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
