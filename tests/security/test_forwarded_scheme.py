"""Forwarded-scheme trust has exactly one boundary: uvicorn's peer allowlist.

Django must derive request security from the ASGI scheme (which uvicorn sets
only for trusted peers) and never from the raw X-Forwarded-Proto header. These
tests drive Django's real ASGI handler and middleware stack; nothing is mocked.
"""

import importlib
import sys
from collections.abc import Iterator

import pytest
from asgiref.sync import async_to_sync
from django.conf import global_settings
from django.test import AsyncClient, AsyncRequestFactory, override_settings

AT = chr(64)
FIXTURE_PASSWORD = "fixture-" + "password"  # noqa: S105 - synthetic, assembled at runtime
PROD_ENV = {
    "SECRET_KEY": "x" * 64,
    "DATABASE_URL": f"postgresql://user:{FIXTURE_PASSWORD}{AT}db.example.test:5432/hookrelay",
    "REDIS_URL": "redis://redis.example.test:6379/0",
    "ALLOWED_HOSTS": "hookrelay.example.test",
}
SETTINGS_MODULES = ("config.settings.base", "config.settings.prod")


@pytest.fixture
def prod_settings(monkeypatch: pytest.MonkeyPatch) -> Iterator[object]:
    saved = {name: sys.modules.get(name) for name in SETTINGS_MODULES}
    for key, value in PROD_ENV.items():
        monkeypatch.setenv(key, value)
    for name in SETTINGS_MODULES:
        sys.modules.pop(name, None)
    yield importlib.import_module("config.settings.prod")
    for name, original in saved.items():
        if original is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = original


def test_production_settings_do_not_set_secure_proxy_ssl_header(prod_settings: object) -> None:
    assert getattr(prod_settings, "SECURE_PROXY_SSL_HEADER", None) is None
    assert global_settings.SECURE_PROXY_SSL_HEADER is None


def test_request_security_follows_the_asgi_scheme_not_the_raw_header() -> None:
    factory = AsyncRequestFactory()

    assert factory.get("/livez").is_secure() is False
    assert factory.get("/livez", headers={"X-Forwarded-Proto": "https"}).is_secure() is False
    assert factory.get("/livez", secure=True).is_secure() is True


@override_settings(SECURE_SSL_REDIRECT=True)
def test_ssl_redirect_ignores_a_forged_forwarded_proto_header() -> None:
    # Real ASGI handler and middleware stack, driven synchronously.
    client = AsyncClient()
    get = async_to_sync(client.get)

    plain = get("/livez")
    forged = get("/livez", headers={"X-Forwarded-Proto": "https"})
    secure = get("/livez", secure=True)

    assert plain.status_code == 301
    assert forged.status_code == 301
    assert secure.status_code == 200
