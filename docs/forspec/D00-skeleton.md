# Förspec D00 — Skeleton

Version 1.5.2 · 2026-09-14 · Status: LOCKED

Amendments in 1.1 (from 1.0): Dockerfile + fly.toml ship in D00 (§2, §4, §6b, §7, §9, §10); local Redis and Postgres via Docker (`compose.yaml`, §11).

Amendments in 1.2 (from 1.1, after static review of the 1453 zip): minimal custom `accounts.User` before the first migration baseline; strict self-only CSP enforced from D00; both htmx 4 fixes (`hx-headers:inherited`, `selfRequestsOnly` removed) with the official upgrade checker as a CI gate; `/livez` + `/readyz` replace `/healthz`; mypy + django-stubs + djangorestframework-stubs as a CI gate; pip-audit and pre-commit locked in the dev group; Bun-native asset copy; future-only dependencies removed; per-app tests plus root cross-cutting tests; `docs/PROOFS.md`. Worker decision unchanged (Tasks for delivery); django-tasks-db, `TASKS` and the `worker` process stay.

Amendments in 1.3 (from 1.2, CI/test hardening only, no domain code): `database_from_url` applies `connect_timeout` last so a URL parameter cannot override it (bug found in review); pytest `--strict-config --strict-markers`, warnings as errors with zero exclusions, branch coverage with a 95% floor; production fail-closed and hardening asserted by tests in D00; PostgreSQL probe-failure and lost-write cache readiness tests; CSP asserted as the complete policy; autouse Redis fixture replaced by opt-in `redis_cache`; `tmp_path: Path`; CI gains pre-commit on the whole tree, `manage.py check`, `check --deploy --fail-level WARNING` (with `SECURE_HSTS_PRELOAD=True` as the header flag), a fresh migration before the boot smoke, hash-verified pip-audit on the production set and on all groups, `bun audit`, `uv tree` evidence, a CycloneDX SBOM artifact, a Docker job that checks the non-root user, migrates, boots and probes the image through the proxy contract, then a Trivy scan (CRITICAL/HIGH, unfixed excluded); every action pinned to a full commit SHA; read-only workflow token with `security-events: write` only for CodeQL; `docs/security/README.md` exception policy; branch ruleset checklist in the README.

Amendments in 1.4 (from 1.3, supply chain only, no application code, no lockfile change): `uv lock --check` as the first gate, `--locked` replaces `--frozen` in CI, security exports and the Dockerfile, `UV_LOCKED=1` workflow-wide (a stale manifest was demonstrated to pass `--frozen` and fail `--locked`); `security.yml` on pull request, push, daily schedule and dispatch with jobs `dependencies` (lock check, both hash-verified pip-audits, `bun audit`, non-blocking `uv audit`, `uv tree`, SBOM), `image` (build + Trivy) and `dependency-review` (PRs, `fail-on-severity: low`); Trivy and the audits leave `ci.yml`; `.github/dependabot.yml` for uv, bun, github-actions, docker and docker-compose; uv 0.11.7, bun 1.4.2, `python:3.14.4-slim`, `oven/bun:1.4.2`, `ghcr.io/astral-sh/uv:0.11.7` pinned; digests added by the owner with the README command; PROOFS wording separates pip-audit (no ignores) from Trivy (`ignore-unfixed`). Required checks: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`.

Amendments in 1.5 (from 1.4, after `security / image` failed on root commit fbae421; container, toolchain and CI only, no application code, no lockfile change): three-stage Dockerfile — assets (Bun, typecheck + build), Python dependency builder (uv 0.12.13, `uv sync --locked --no-dev`, collectstatic), runtime (same `PYTHON_IMAGE` reference, explicit COPY of `.venv`, `manage.py`, `config`, `apps`, `templates`, `static/dist`, `staticfiles`, user `app`); no uv/uvx/Bun/caches/compilers/dev dependencies in the runtime; no `apt-get upgrade`; system pip kept; Python 3.14.7 from `.python-version` everywhere (CI omits the version input, Docker takes `ARG PYTHON_IMAGE`, `tests/integration/test_toolchain.py` pins the interpreter); uv 0.12.13 across setup-uv and the uv image, `uv audit` invocation corrected; Trivy fail-closed on CRITICAL/HIGH with vuln + secret scanners, no `ignore-unfixed`, plus a runtime-image CycloneDX SBOM; `ci / docker` gains a no-cache build, runtime-clean gate, interpreter gate, setuid/setgid allowlist gate (`docker/suid-allowlist.txt`, measured by the owner), migrate through the image and a two-way forwarded-header trust probe on the bridge network; `--forwarded-allow-ips=*` removed everywhere, trust comes from `FORWARDED_ALLOW_IPS` (default loopback), Fly value measured at first deploy; `bun run typecheck:tools` blocking in `ci / test`; `.env.example` restored (55433/56380); `.dockerignore` tightened. Superseded text below in §6b is replaced by this paragraph.

Corrections in 1.5.1 (acceptance issues from the static review of the 1.5 zip; nothing else): the Dockerfile owns the complete `PYTHON_IMAGE` reference and no workflow or README command passes a build-arg for it (a digest pin therefore applies to every build); `tests/integration/test_toolchain.py` also asserts the Dockerfile's `PYTHON_IMAGE` version equals `.python-version`, with or without `@sha256`; Trivy engine `v0.74.0` on both action invocations; runtime SBOM produced and uploaded before the fail-closed scan; `docs/security/README.md` rewritten to the fixed-or-unfixed policy; PROOFS wording made precise (workflow token default read-only, CodeQL scoped write; digest pins GATE DEFINED); production deploy blocked until the Fly trust range is established from documented behaviour or a staged deployment proof; secret-scanning addendum — no credential-shaped URI literal committed, fixtures assembled at runtime, `tests/security/test_repository_hygiene.py` as a fail-closed gate over the whole tree with loopback/container-local placeholders as the documented exception.

Amendments in 1.5.2 (runtime family selection from the owner's local image proof; container, CI and tests only, no application code, no lockfile change): the Debian runtime, the `/usr/local/bin/python3.14` same-image rule, the `apt` discussion, the Debian SUID allowlist, Alpine and pip removal are all superseded. Four-stage Dockerfile — uv source, Bun assets, Chainguard `python:latest-dev` builder (uv against `/usr/bin/python`, `uv sync --locked --no-dev`, collectstatic), Chainguard `python:latest` runtime (65532, no shell, `ENTRYPOINT []`, absolute uvicorn CMD, explicit `COPY --chown=65532:65532`); every image reference an owner-measured index digest incl. `postgres:17`/`redis:7` in compose and CI (`tests/security/test_image_references.py` refuses tag-only); `scripts/inspect_rootfs.py` inspects the exported rootfs on the host (no shell, tooling, package managers, caches, tests/docs/.env, dev packages; zero setuid/setgid; required files present); CI proves user 65532, Python 3.14.7 from `/app/.venv` with django/psycopg/uvloop/httptools, migrate, boot, `/livez`, `/readyz` and the two-way trust boundary without a shell; `.python-version` is a static invariant (3.14.7); hygiene gate tightened to explicit reviewed fixtures in approved contexts; Trivy action keeps `vuln-type` (maps to `--pkg-types`); README/PROOFS precision; ruleset marked OPEN owner action.

## 1. Goal

A runnable, CI-green skeleton with the locked stack and layout, zero domain code. Everything Drop 1+ builds on is decided here so later drops touch only `apps/`.

## 2. Locked decisions carried in

- Queue: Django tasks framework + `django-tasks-db` (`id_function: uuid.uuid7`).
- Live stream and cache: Redis (Upstash in prod) via `redis` (redis-py). Cache backend = `RedisCache` from day one so throttling is cross-process later.
- Ids: bigint PK + UUIDv7 `public_id` (`uuid.uuid7()`, Python 3.14).
- HTTP client: httpx sync. No async views until Drop 5 (SSE), where it is motivated.
- Partitioning of DeliveryAttempt: Drop 7, measured first (GraphQL is Drop 6).
- Dockerfile + fly.toml in D00; no deploy performed in D00.
- Local Postgres and Redis run as Docker containers (`compose.yaml`).
- `AUTH_USER_MODEL = "accounts.User"` (`class User(AbstractUser): pass`, nothing more). Application code uses `settings.AUTH_USER_MODEL` / `get_user_model()`, never `django.contrib.auth.models.User`.
- CSP enforced from D00 with a strict self-only baseline; no nonce until an inline requirement is proven. Consequence: no DRF browsable API (JSON + OpenAPI is the contract).
- A dependency enters the lockfile in the drop whose code or tests first use it.

## 3. Dependencies

Python (uv; exact versions in `uv.lock` and LEVERANS): django 6.1, djangorestframework 3.18, psycopg[binary], django-tasks-db, redis, django-htmx, drf-spectacular, uvicorn[standard]. Dev group: pytest, pytest-django, pytest-cov, ruff, mypy, django-stubs, djangorestframework-stubs (kept because it passes strict mypy against the exact lock), pip-audit, pre-commit. Deferred to the drop that first uses them: django-filter (D04), httpx and respx (D03), time-machine (D03), factory-boy (when factories earn their place).
Bun: tailwindcss, @tailwindcss/cli, htmx.org 4.0.0 (pinned explicitly — npm `latest` is still 2.x), @alpinejs/csp.
No `pool` extra on psycopg yet — enabled in Drop 6 with a measurement.

## 4. FILES TO TOUCH (authoritative)

```
hookrelay/
  .env.example  .gitignore  .dockerignore  .pre-commit-config.yaml  README.md
  pyproject.toml  uv.lock  package.json  bun.lock  manage.py
  Dockerfile  fly.toml  compose.yaml
  .github/workflows/ci.yml  .github/workflows/codeql.yml  .github/workflows/security.yml  .github/dependabot.yml
  config/__init__.py  config/asgi.py  config/wsgi.py  config/urls.py  config/views.py
  config/settings/__init__.py  base.py  dev.py  test.py  prod.py
  apps/__init__.py
  templates/base.html  templates/index.html
  static/src/app.css  static/src/app.js  static/dist/.gitkeep
  tests/__init__.py  tests/conftest.py  tests/test_skeleton.py
  docs/forspec/D00-skeleton.md  docs/LEVERANS-D00.md
```

## 5. Settings design

- `base.py`: `USE_TZ`, UTC, `BigAutoField`, `AUTH_USER_MODEL`. `DATABASE_URL` parsed with `urlsplit` (query params pass through to libpq; `connect_timeout=3` bounds readiness). `REDIS_URL` → `CACHES` (`RedisCache`, `socket_connect_timeout`/`socket_timeout` 2 s — verified to reach redis-py's pool through `OPTIONS`). `TASKS` → `django_tasks_db.DatabaseBackend` with `id_function: uuid.uuid7`. Verified at build: neither Django 6.1 core nor django-tasks-db 0.13.0 has an enqueue-on-commit option; `enqueue()` is a plain `objects.create()`, so an enqueue inside `transaction.atomic()` commits or rolls back with the surrounding rows by construction. `ContentSecurityPolicyMiddleware` + `SECURE_CSP` (default/script/style/connect/font `'self'`, img `'self' data:`, object and frame-ancestors `'none'`, base-uri and form-action `'self'`). `REST_FRAMEWORK`: `IsAuthenticated` default (deny by default), JSON renderer/parser only, spectacular schema class. `STATICFILES_DIRS=[static/dist]`; prod `STORAGES` uses `ManifestStaticFilesStorage`. Middleware includes `django_htmx`. Logging → stdout.
- `dev.py`: `DEBUG=True`, compose defaults for `DATABASE_URL`/`REDIS_URL`, `staticfiles_urlpatterns()` so uvicorn serves assets in development. No browsable API.
- `test.py`: `TASKS` → `ImmediateBackend`; compose defaults with Redis db 1; fast hasher.
- `prod.py`: fails closed without `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `ALLOWED_HOSTS`; `SECURE_*` headers; `SECURE_PROXY_SSL_HEADER` for Fly.

## 6. Frontend pipeline

`package.json` scripts: `build:css`, `watch:css`, `build:js` (`bun scripts/copy-assets.ts` — Bun-native copy of htmx, the Alpine CSP build and `app.js` into `static/dist/` as four separate files, identical on Windows and Linux, no bundler), `build`, `htmx:check` (the official htmx 4 upgrade checker over `templates static/src apps`; exits 1 on findings). `static/dist/` is gitignored and built in CI and in the image. `base.html` loads the three assets and sets `hx-headers:inherited` for CSRF (htmx 4 inheritance is explicit); `app.js` contains no code. `index.html` proves the pipeline at `/`.

## 6b. Image and Fly

Multi-stage Dockerfile: bun stage builds assets; python:3.14-slim stage runs `uv sync --frozen --no-dev`, copies `static/dist/`, runs `collectstatic` at build with placeholder env, non-root user, uvicorn on 8080 with `--proxy-headers`. `fly.toml`: placeholder app name, `web` and `worker` (`db_worker`) processes, `release_command = migrate --noinput`, `/readyz` HTTP check, `[[statics]]` serving `/app/staticfiles` at `/static/`. Secrets are set by the operator; no deploy in D00.

## 7. CI and hooks

`ci.yml` (token `contents: read`): job `test` — postgres:17 + redis:7 services; frozen uv/bun installs; asset build; `pre-commit run --all-files --show-diff-on-failure`; ruff check + format --check; `mypy .` (strict); `bun run htmx:check`; `manage.py check`; `manage.py check --deploy --fail-level WARNING` under production settings with CI-only values; `makemigrations --check --dry-run`; `migrate --noinput` against the CI database; `pytest -m "not slow and not e2e"` (warnings as errors, branch coverage ≥ 95% via addopts; the `slow and not e2e` concurrency lane is added as a job with the first slow test); uvicorn boot smoke on `/readyz` and `/livez`. Job `security` — `uv export` with hashes for the production set and for `--all-groups`, each audited with `pip-audit --strict --require-hashes`; `bun audit`; `uv tree --all-groups`; CycloneDX SBOM uploaded as an artifact. Job `docker` — build; `USER` must be `app`; migrate with the image; boot the image and probe `/readyz` and `/` with `X-Forwarded-Proto: https` (the Fly proxy contract); Trivy scan CRITICAL/HIGH with `ignore-unfixed`, exit 1. `codeql.yml`: python + javascript-typescript, `security-events: write` only there. All actions pinned to full commit SHAs resolved from the repositories (tag in a trailing comment). `.pre-commit-config.yaml`: pre-commit-hooks v6.0.0 (check-yaml, end-of-file-fixer, trailing-whitespace, mixed-line-ending --fix=lf) plus local `uv run ruff check --fix --force-exclude` / `uv run ruff format --force-exclude` so hook and lockfile share one ruff version and generated migrations keep Django's formatting. Superseded in 1.4: audits and Trivy live in `security.yml`; required checks are `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`.

## 8. Tests (≈20, real count measured after build)

Layout: app behaviour in `apps/<app>/tests/`, cross-component guarantees in `tests/{integration,concurrency,system,security}/`; `testpaths = ["apps", "tests"]`. Redis is opt-in via the `redis_cache` fixture; ordinary tests never touch it.

`tests/integration/test_skeleton.py`: `/livez` with zero queries; `/readyz` ok (Redis opt-in); `/readyz` 503 with unreachable Redis, location absent from the body; `/readyz` 503 when the PostgreSQL probe raises, detail in the log and absent from the body; `/readyz` 503 when the cache loses writes (DummyCache); `POST /readyz` → 405; index references the stylesheet; static files resolvable only under `DEBUG=True`; CSP equals the complete intended policy; no missing migrations; schema warning-free.

`tests/integration/test_settings.py`: URL query parameters pass through to libpq; `connect_timeout` cannot be overridden by the URL; production import fails closed for each of `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `ALLOWED_HOSTS` (parametrised); fully configured production has `DEBUG=False`, SSL redirect, secure cookies, HSTS > 0 with subdomains and preload, proxy header, CSP middleware and policy, manifest static storage; development defaults match compose.

`apps/accounts/tests/test_user_model.py`: `AUTH_USER_MODEL` is `accounts.User`, `get_user_model()` returns it, a row persists.

Baseline: BEFORE (1525 zip) = 9/0/0. AFTER measured and reported in LEVERANS.

## 9. NOT in D00

Domain models beyond the bare user, auth flows, API endpoints beyond the schema route, a task definition, SSE, connection pooling, GraphQL, partitioning, an actual deployment, Fly secrets, a CSP nonce, a browsable API.

## 10. BEVISAR / BEVISAR INTE

BEVISAR: the pinned stack installs, type-checks and boots under uvicorn on a freshly migrated database; the swappable user exists from the first migration; `/livez` needs no dependency, `/readyz` proves PostgreSQL and Redis with bounded probes and degrades correctly for an unreachable Redis, a failing PostgreSQL probe and a lossy cache, leaking nothing; the CSP is exactly the intended policy; production settings fail closed for each required value and are hardened when configured; the enforced connection timeout survives URL parameters; the tree carries no htmx 2 residue; warnings are errors and the suite has none; branch coverage is at least 95%; hooks, ruff, mypy, pip-audit with hashes on both sets, bun audit and the Django system and deploy checks are CI gates; the image runs as non-root, migrates, boots and answers through the proxy contract; every action is SHA-pinned under a read-only token.
BEVISAR INTE: task execution (no task defined; Drop 3); an htmx request under the CSP in a browser (Drop 5); a dead PostgreSQL server (the probe test raises the driver error; the Redis test is the real-outage proof); Windows behaviour of the Bun script until run there; the Docker job and Trivy result until GitHub runs them; PostgreSQL 17 specifically (sandbox ran 16).

## 11. Ritual (pwsh 7)

```
docker compose up -d
uv sync && bun install && bun run build && uv run python manage.py migrate && uv run pytest -m "not e2e" --no-cov
uv run ruff check . && uv run ruff format --check . && uv run mypy . && bun run htmx:check && uv run python manage.py check
uv run uvicorn config.asgi:application --reload
```
Supply-chain checks run the same way locally when a dependency changes: `uv export --frozen --no-dev --no-emit-project -o req.txt && uv run pip-audit --strict --require-hashes -r req.txt && bun audit`.
