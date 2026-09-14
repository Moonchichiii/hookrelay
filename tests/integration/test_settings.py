"""Settings contracts and production fail-closed behavior."""

import importlib
import sys
from collections.abc import Callable, Iterator
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings.base import database_from_url

PROD_ENV = {
    "SECRET_KEY": "x" * 64,
    "DATABASE_URL": "postgresql://user:pw@db.example.test:5432/hookrelay?sslmode=require",
    "REDIS_URL": "rediss://default:pw@redis.example.test:6379/0",
    "ALLOWED_HOSTS": "hookrelay.example.test,www.hookrelay.example.test",
}
ENV_KEYS = ("SECRET_KEY", "DATABASE_URL", "REDIS_URL", "ALLOWED_HOSTS", "LOG_LEVEL")
SETTINGS_MODULES = ("config.settings.base", "config.settings.dev", "config.settings.prod")

LoadSettings = Callable[[str, dict[str, str]], ModuleType]


@pytest.fixture
def load_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[LoadSettings]:
    saved = {name: sys.modules.get(name) for name in SETTINGS_MODULES}

    def _load(module: str, env: dict[str, str]) -> ModuleType:
        for key in ENV_KEYS:
            monkeypatch.delenv(key, raising=False)
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        for name in SETTINGS_MODULES:
            sys.modules.pop(name, None)
        return importlib.import_module(module)

    yield _load

    for name, original in saved.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


def test_database_url_query_parameters_pass_through_to_libpq() -> None:
    config = database_from_url("postgresql://u:p%40ss@host.example.test:6543/db?sslmode=require")

    assert config["NAME"] == "db"
    assert config["USER"] == "u"
    assert config["PASSWORD"] == "p@ss"  # noqa: S105 - URL-parsing fixture, not a credential
    assert config["HOST"] == "host.example.test"
    assert config["PORT"] == "6543"
    assert config["OPTIONS"]["sslmode"] == "require"


def test_database_url_cannot_override_the_enforced_connect_timeout() -> None:
    config = database_from_url("postgresql://u:p@host.example.test/db?connect_timeout=60")

    assert config["OPTIONS"]["connect_timeout"] == 3


@pytest.mark.parametrize("missing", ["SECRET_KEY", "DATABASE_URL", "REDIS_URL", "ALLOWED_HOSTS"])
def test_production_settings_fail_closed_without_each_required_value(
    load_settings: LoadSettings, missing: str
) -> None:
    env = {key: value for key, value in PROD_ENV.items() if key != missing}

    with pytest.raises(ImproperlyConfigured, match=missing):
        load_settings("config.settings.prod", env)


def test_production_settings_are_hardened_when_fully_configured(
    load_settings: LoadSettings,
) -> None:
    prod = load_settings("config.settings.prod", PROD_ENV)

    assert prod.DEBUG is False
    assert prod.ALLOWED_HOSTS == ["hookrelay.example.test", "www.hookrelay.example.test"]
    assert prod.CSRF_TRUSTED_ORIGINS == [
        "https://hookrelay.example.test",
        "https://www.hookrelay.example.test",
    ]
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.SESSION_COOKIE_SECURE is True
    assert prod.CSRF_COOKIE_SECURE is True
    assert prod.SECURE_HSTS_SECONDS > 0
    assert prod.SECURE_HSTS_INCLUDE_SUBDOMAINS is True
    assert prod.SECURE_HSTS_PRELOAD is True
    assert prod.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
    assert "django.middleware.csp.ContentSecurityPolicyMiddleware" in prod.MIDDLEWARE
    assert prod.SECURE_CSP["default-src"] == ["'self'"]
    assert prod.DATABASES["default"]["OPTIONS"] == {"sslmode": "require", "connect_timeout": 3}
    assert prod.STORAGES["staticfiles"]["BACKEND"].endswith("ManifestStaticFilesStorage")


def test_development_settings_default_to_the_compose_services(
    load_settings: LoadSettings,
) -> None:
    dev = load_settings("config.settings.dev", {})

    assert dev.DEBUG is True
    assert dev.DATABASES["default"]["HOST"] == "127.0.0.1"
    assert dev.DATABASES["default"]["NAME"] == "hookrelay"
    assert dev.CACHES["default"]["LOCATION"] == "redis://127.0.0.1:56380/0"
    assert dev.CACHES["default"]["OPTIONS"] == {"socket_connect_timeout": 2, "socket_timeout": 2}
