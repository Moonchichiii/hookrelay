"""Settings contracts: URL parsing invariants and production fail-closed behaviour.

Settings modules read the environment at import time, so each test imports a
fresh copy under a controlled environment and restores the originals afterwards.
django.conf.settings is untouched: it copied its values at start-up.

Fixture connection URLs are assembled at runtime from synthetic parts so no
credential-shaped literal is ever committed (GitHub secret scanning reads
source text, not runtime values).
"""

import importlib
import sys
from collections.abc import Callable, Iterator
from types import ModuleType

import pytest
from django.core.exceptions import ImproperlyConfigured

from config.settings.base import database_from_url

FIXTURE_PASSWORD = "fixture-" + "password"  # noqa: S105 - synthetic, assembled at runtime
AT = chr(64)


def dsn(scheme: str, user: str, password: str, host: str, path: str) -> str:
    return f"{scheme}://{user}:{password}{AT}{host}{path}"


PROD_ENV = {
    "SECRET_KEY": "x" * 64,
    "DATABASE_URL": dsn(
        "postgresql", "user", FIXTURE_PASSWORD, "db.example.test:5432", "/hookrelay?sslmode=require"
    ),
    "REDIS_URL": dsn("rediss", "default", FIXTURE_PASSWORD, "redis.example.test:6379", "/0"),
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
    # The password carries a percent-encoded "@" so the parser's decoding is
    # covered; both the encoded and the expected decoded form are built here.
    encoded_password = "p%40" + "ss"
    url = dsn("postgresql", "u", encoded_password, "host.example.test:6543", "/db?sslmode=require")

    config = database_from_url(url)

    assert config["NAME"] == "db"
    assert config["USER"] == "u"
    assert config["PASSWORD"] == "p" + AT + "ss"
    assert config["HOST"] == "host.example.test"
    assert config["PORT"] == "6543"
    assert config["OPTIONS"]["sslmode"] == "require"


def test_database_url_cannot_override_the_enforced_connect_timeout() -> None:
    url = dsn("postgresql", "u", FIXTURE_PASSWORD, "host.example.test", "/db?connect_timeout=60")

    config = database_from_url(url)

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
    assert not hasattr(prod, "SECURE_PROXY_SSL_HEADER")
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
    assert dev.DATABASES["default"]["PORT"] == "55433"
    assert dev.DATABASES["default"]["NAME"] == "hookrelay"
    assert dev.CACHES["default"]["LOCATION"] == "redis://127.0.0.1:56380/0"
    assert dev.CACHES["default"]["OPTIONS"] == {"socket_connect_timeout": 2, "socket_timeout": 2}
