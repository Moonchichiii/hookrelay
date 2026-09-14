import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import DATABASES, REDIS_URL, SECRET_KEY

for name, value in (
    ("SECRET_KEY", SECRET_KEY),
    ("DATABASE_URL", DATABASES["default"]["NAME"]),
    ("REDIS_URL", REDIS_URL),
    ("ALLOWED_HOSTS", os.environ.get("ALLOWED_HOSTS", "")),
):
    if not value:
        raise ImproperlyConfigured(f"{name} must be set in production")

DEBUG = False
ALLOWED_HOSTS = os.environ["ALLOWED_HOSTS"].split(",")
CSRF_TRUSTED_ORIGINS = [f"https://{host}" for host in ALLOWED_HOSTS]

# Fly terminates TLS at the edge and forwards the original scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# Header flag only; the domain is not submitted to the preload list by this.
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}
