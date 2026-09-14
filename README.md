# hookrelay

A webhook delivery service: tenants publish events over an API and hookrelay delivers them to subscriber endpoints with HMAC signatures, retries with backoff, per-endpoint circuit breakers, a dead-letter queue, replay, and a live delivery log.

Small domain, deep backend. The interesting parts are transactions, idempotency, worker concurrency, tamper-evident audit and throughput — not the schema.

## Stack

Python 3.14 · Django 6.1 · Django REST Framework 3.18 · PostgreSQL 17 · Redis 7 · django-tasks-db (Django's tasks framework, database backend) · django-htmx + htmx 4 · Alpine.js (CSP build, local UI state only) · Tailwind CSS 4 · uv · bun · uvicorn · Fly.io

## Run it locally

Prerequisites: uv, bun, Docker (for Postgres and Redis). PowerShell 7 examples; the `&&` chains stop on the first error.

```
docker compose up -d
uv sync && bun install && bun run build && uv run python manage.py migrate && uv run pytest -m "not e2e" --no-cov
uv run uvicorn config.asgi:application --reload
```

Quality gate (same as CI):

```
uv lock --check && uv run ruff check . && uv run ruff format --check . && uv run mypy . && bun run htmx:check && uv run python manage.py check
```

Then open http://127.0.0.1:8000/, /livez (process only) and /readyz (PostgreSQL + Redis). The dev and test settings default to the compose credentials; copy `.env.example` to `.env` and run commands with `uv run --env-file .env ...` only if you point at something else.

Hooks: `uv run pre-commit install` once, then they run on staged files.

## Layout

```
config/     settings (base/dev/test/prod), asgi, urls, project-level views
apps/       one Django app per bounded area, each with models / services / selectors / api
templates/  base.html and page templates
static/src  Tailwind input and global JS; static/dist is built by bun and not committed
apps/<app>/tests/  behaviour of that app
tests/      cross-component guarantees: integration/, concurrency/, system/, security/
scripts/    Bun build helpers
docs/       förspec per drop, delivery notes (LEVERANS) and the proof registry (PROOFS.md)
```

## Quality gates

`ci.yml` enforces, on every push and pull request: `uv lock --check` and `--locked` installs (a stale lock fails; `UV_LOCKED=1` applies to every uv call), a frozen bun install, the asset build, pre-commit on the whole tree, ruff check and format, mypy strict, the htmx 4 upgrade checker, `manage.py check`, `check --deploy --fail-level WARNING` under production settings, migration drift, a fresh migration, the fast test lane with warnings as errors and a branch-coverage floor of 95%, a uvicorn boot smoke on the migrated database, and a Docker build that must run as non-root, migrate and answer `/readyz` and `/` through the proxy contract.

`security.yml` runs on every change **and daily**: hash-verified pip-audit on the production set and on all dependency groups (no ignores — see `docs/security/README.md`), `bun audit`, `uv audit` as a non-blocking secondary signal, a Python SBOM artifact, a Trivy scan of the image (CRITICAL/HIGH, unfixed excluded), and GitHub's dependency review on pull requests. `codeql.yml` covers Python and JavaScript. Every GitHub Action is pinned to a full commit SHA, uv and bun are pinned to exact versions, base images to exact tags, and the workflow token is read-only.

Rules that do not move: a later drop never weakens an earlier gate to get green. `# type: ignore`, `# noqa` and coverage exclusions name the narrowest scope and the reason on the same line. Warnings are errors; an exclusion names the exact warning. Flaky concurrency tests are fixed at the race, never retried. Vulnerability exceptions follow `docs/security/README.md`. The claim → evidence registry lives in `docs/PROOFS.md`.

### Branch ruleset for `main` (configured in GitHub, not in code)

Pull request required (0 approvals for a solo developer is fine), required status checks with the branch up to date: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`; conversations resolved; force pushes and deletion blocked; no bypass for normal work. The PR is the evidence envelope for every change.

### Repository settings (GitHub, not code)

Dependency graph on; Dependabot alerts on; Dependabot security updates on (`.github/dependabot.yml` covers the weekly version updates for uv, bun, GitHub Actions, Docker and compose). The `uv` and `bun` ecosystems are confirmed by Dependabot's first run.

### Image digests

Base and service images are pinned to exact tags. To pin them to digests as well (then Dependabot keeps the digests current), run once with Docker available and replace `image:tag` with the printed `image@sha256:…` form in `Dockerfile`, `.github/workflows/ci.yml`, `.github/workflows/security.yml` and `compose.yaml`:

```
foreach ($i in "python:3.14.4-slim","oven/bun:1.4.2","ghcr.io/astral-sh/uv:0.11.7","postgres:17","redis:7") { docker pull -q $i | Out-Null; docker image inspect --format '{{index .RepoDigests 0}}' $i }
```

## Deploy

The image is built by the Dockerfile (bun stage for assets, uv stage for Python, `collectstatic` at build). Fly runs `web` (uvicorn) and `worker` (`db_worker`) process groups, `migrate` as the release command, and serves `/static/` straight from the image via `[[statics]]`. Secrets: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `ALLOWED_HOSTS`.
