import importlib
import logging
from collections.abc import Iterator
from pathlib import Path

import pytest
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError
from django.test import Client, override_settings
from django.urls import Resolver404, clear_url_caches, resolve, reverse
from pytest_django import DjangoAssertNumQueries

import config.urls

pytestmark = pytest.mark.django_db

EXPECTED_CSP = {
    "default-src": ["'self'"],
    "script-src": ["'self'"],
    "style-src": ["'self'"],
    "connect-src": ["'self'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "object-src": ["'none'"],
    "base-uri": ["'self'"],
    "frame-ancestors": ["'none'"],
    "form-action": ["'self'"],
}


def test_livez_is_ok_without_touching_the_database(
    client: Client, django_assert_num_queries: DjangoAssertNumQueries
) -> None:
    with django_assert_num_queries(0):
        response = client.get(reverse("livez"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.usefixtures("redis_cache")
def test_readyz_reports_db_and_redis_ok(client: Client) -> None:
    response = client.get(reverse("readyz"))

    assert response.status_code == 200
    assert response["Content-Type"] == "application/json"
    assert response.json() == {"status": "ok", "db": "ok", "redis": "ok"}


UNREACHABLE_REDIS_PASSWORD = "fixture-" + "password"  # noqa: S105 - synthetic, assembled at runtime


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            # Unreachable Redis must fail fast without leaking the location.
            "LOCATION": f"redis://:{UNREACHABLE_REDIS_PASSWORD}{chr(64)}127.0.0.1:9/1",
            "OPTIONS": {"socket_connect_timeout": 1, "socket_timeout": 1},
        }
    }
)
def test_readyz_degrades_when_redis_is_unreachable(client: Client) -> None:
    response = client.get(reverse("readyz"))

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "db": "ok", "redis": "error"}
    assert UNREACHABLE_REDIS_PASSWORD not in response.content.decode()


@pytest.mark.usefixtures("redis_cache")
def test_readyz_degrades_when_the_database_probe_fails(
    client: Client, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    # Database details belong in logs, never in the response.
    marker = "db-detail-must-not-leak"

    def failing_cursor() -> None:
        raise OperationalError(f"connection failed: {marker}")

    monkeypatch.setattr(connections["default"], "cursor", failing_cursor)

    with caplog.at_level(logging.ERROR, logger="config.views"):
        response = client.get(reverse("readyz"))

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "db": "error", "redis": "ok"}
    assert marker not in response.content.decode()
    assert marker in caplog.text


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}})
def test_readyz_treats_a_cache_that_loses_writes_as_an_error(client: Client) -> None:
    response = client.get(reverse("readyz"))

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "db": "ok", "redis": "error"}


def test_readyz_rejects_post(client: Client) -> None:
    assert client.post(reverse("readyz")).status_code == 405


def test_index_renders_with_built_stylesheet(client: Client) -> None:
    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert "/static/app.css" in response.content.decode()


@pytest.fixture
def reloaded_urlconf() -> Iterator[None]:
    clear_url_caches()
    yield
    importlib.reload(config.urls)
    clear_url_caches()


@pytest.mark.usefixtures("reloaded_urlconf")
def test_static_files_are_served_by_django_only_in_debug() -> None:
    with override_settings(DEBUG=True):
        importlib.reload(config.urls)
        clear_url_caches()
        assert resolve("/static/app.css").url_name is None

    with override_settings(DEBUG=False):
        importlib.reload(config.urls)
        clear_url_caches()
        with pytest.raises(Resolver404):
            resolve("/static/app.css")


def test_csp_header_is_exactly_the_intended_policy(client: Client) -> None:
    policy = client.get(reverse("index"))["Content-Security-Policy"]
    directives = {d.split()[0]: d.split()[1:] for d in policy.split(";") if d.strip()}

    assert directives == EXPECTED_CSP


def test_no_migrations_are_missing() -> None:
    call_command("makemigrations", "--check", "--dry-run", verbosity=0)


def test_schema_generates_without_warnings(tmp_path: Path) -> None:
    # The schema contract is warning-free.
    call_command(
        "spectacular",
        "--fail-on-warn",
        "--validate",
        file=str(tmp_path / "schema.yml"),
        verbosity=0,
    )
