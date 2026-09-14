"""Project-level views: the index page and the health probes. Domain views live in apps/."""

import logging

from django.core.cache import cache
from django.db import connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)


@require_GET
def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


# Exemption lets require_GET return 405 for stray POSTs instead of CSRF returning 403.


@csrf_exempt
@require_GET
def livez(request: HttpRequest) -> JsonResponse:
    # Do not couple process liveness to dependency availability.
    return JsonResponse({"status": "ok"})


@csrf_exempt
@require_GET
def readyz(request: HttpRequest) -> JsonResponse:
    # Return probe names to clients while keeping connection details in logs.
    checks = {"db": _check_db(), "redis": _check_redis()}
    ok = all(status == "ok" for status in checks.values())
    return JsonResponse({"status": "ok" if ok else "degraded", **checks}, status=200 if ok else 503)


def _check_db() -> str:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        logger.exception("readyz: database probe failed")
        return "error"
    return "ok"


def _check_redis() -> str:
    try:
        cache.set("readyz", "ok", timeout=5)
        if cache.get("readyz") != "ok":
            return "error"
    except Exception:
        logger.exception("readyz: redis probe failed")
        return "error"
    return "ok"
