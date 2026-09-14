# hookrelay

A webhook delivery service: tenants publish events over an API and hookrelay delivers them to subscriber endpoints with HMAC signatures, retries with backoff, per-endpoint circuit breakers, a dead-letter queue, replay, and a live delivery log.

Small domain, deep backend. The interesting parts are transactions, idempotency, worker concurrency, tamper-evident audit and throughput — not the schema.

## Stack

Python 3.14.7 (`.python-version`) · Django 6.1 · Django REST Framework 3.18 · PostgreSQL 17 · Redis 7 · django-tasks-db (Django's tasks framework, database backend) · django-htmx + htmx 4 · Alpine.js (CSP build, local UI state only) · Tailwind CSS 4 · uv · bun · uvicorn · Fly.io

## Run it locally

Prerequisites: uv, bun, Docker (for Postgres and Redis). PowerShell 7 examples; the `&&` chains stop on the first error.

```
docker compose up -d
uv sync && bun install && bun run build && uv run python manage.py migrate && uv run pytest -m "not e2e" --no-cov
uv run uvicorn config.asgi:application --reload
```

Quick local quality subset (CI runs the complete wall described under Quality gates):

```
uv lock --check && uv run ruff check . && uv run ruff format --check . && uv run mypy . && bun run typecheck:tools && bun run htmx:check && uv run python manage.py check
```

Then open http://127.0.0.1:8000/, /livez (process only) and /readyz (PostgreSQL + Redis). The dev and test settings default to the compose services (PostgreSQL on host port 55433, Redis on 56380); copy `.env.example` to `.env` and run commands with `uv run --env-file .env ...` only if you point at something else. `.env` is git-ignored and never enters the Docker build context.

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

`ci.yml` enforces, on every push and pull request: `uv lock --check` and `--locked` installs (a stale lock fails; `UV_LOCKED=1` applies to every uv call), a frozen bun install, `bun run typecheck:tools`, the asset build, pre-commit on the whole tree, ruff check and format, mypy strict, the htmx 4 upgrade checker, `manage.py check`, `check --deploy --fail-level WARNING` under production settings, migration drift, a fresh migration, the fast test lane with warnings as errors and a branch-coverage floor of 95%, a uvicorn boot smoke on the migrated database, and the final-image gates: a no-cache Docker build, runtime user `65532`, host-side inspection of the exported rootfs (no shell, no uv/uvx/Bun/node/compilers/package managers, no tests/docs/.env/caches, no dev packages in the venv, zero setuid/setgid files), Python 3.14.7 executing from `/app/.venv` with django/psycopg/uvloop/httptools importable, migrate and boot through the final image, `/livez` and `/readyz`, and the forwarded-header trust boundary proven both ways on the bridge network.

`security.yml` runs on every change **and daily**: hash-verified pip-audit on the production set and on all dependency groups (no ignores — see `docs/security/README.md`), `bun audit`, `uv audit` as a non-blocking secondary signal, a Python lock SBOM, a Trivy scan of the final runtime image that fails on any known unsuppressed CRITICAL or HIGH finding (vuln + secret scanners, OS + library, no `ignore-unfixed`, no ignore file), a CycloneDX SBOM of that image, and GitHub's dependency review on pull requests. `codeql.yml` covers Python and JavaScript. Every GitHub Action is pinned to a full commit SHA; uv 0.12.13, bun 1.4.2 and Python 3.14.7 (`.python-version`) are pinned; every base and service image is pinned by index digest (`tests/security/test_image_references.py` refuses tag-only references); the workflow token defaults to `contents: read`, with CodeQL alone receiving the scoped `security-events: write` it requires.

No unapproved credential-shaped connection URI is committed: test fixtures assemble DSNs at runtime, and `tests/security/test_repository_hygiene.py` fails the suite if a literal `scheme://user:password@host` appears anywhere in the tree unless it is one of the explicit reviewed synthetic combinations (the compose credentials `hookrelay:hookrelay` on the local service hosts, the build-only `build:build@localhost`) in an approved context (development settings, `.env.example`, CI services, Dockerfile, README, evidence docs). A loopback host is not an exemption by itself. The same check by hand: `git grep -n -E '(postgres(ql)?|redis(s)?)://[^[:space:]/:@]*:[^[:space:]@]+@'` should list only those fixtures.

Rules that do not move: a later drop never weakens an earlier gate to get green. `# type: ignore`, `# noqa` and coverage exclusions name the narrowest scope and the reason on the same line. Warnings are errors; an exclusion names the exact warning. Flaky concurrency tests are fixed at the race, never retried. Vulnerability exceptions follow `docs/security/README.md`. The claim → evidence registry lives in `docs/PROOFS.md`.

### Branch ruleset for `main` — OWNER ACTION, OPEN

Not configured yet as of D00 v1.5.2 (repository inspection showed no ruleset; classic branch protection was not inspectable). Until the owner configures and verifies it, nothing in this repository claims the branch is protected. Target: pull request required (0 approvals for a solo developer is fine), required status checks with the branch up to date: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`; conversations resolved; force pushes and deletion blocked; no bypass for normal work. The PR is the evidence envelope for every change.

### Repository settings (GitHub, not code)

Dependency graph on; Dependabot alerts on; Dependabot security updates on (`.github/dependabot.yml` covers the weekly version updates for uv, bun, GitHub Actions, Docker and compose). The `uv` and `bun` ecosystems are confirmed by Dependabot's first run.

### Runtime image (Docker required)

Four stages — uv source → frontend assets (Bun) → Python dependency builder (Chainguard `python:latest-dev`, uv, `uv sync --locked --no-dev`, collectstatic) → minimal runtime (Chainguard `python:latest`: no shell, no package manager, non-root UID 65532, only `/app/.venv` and the application paths). Every image is pinned by index digest in the Dockerfile (`ARG PYTHON_BUILDER_IMAGE`, `PYTHON_RUNTIME_IMAGE`, `UV_IMAGE`, `BUN_IMAGE`); the compose and CI service images likewise (`postgres:17` measured as 17.11, `redis:7` as 7.4.11). Digests are refreshed only deliberately, with a rescan, never by CI.

Prove the final image locally exactly as CI does (pwsh):

```
docker build --no-cache -t hookrelay:ci .
docker inspect --format '{{.Config.User}}' hookrelay:ci
docker create --name hookrelay-inspect hookrelay:ci; docker export hookrelay-inspect -o hookrelay-rootfs.tar; docker rm hookrelay-inspect; uv run python scripts/inspect_rootfs.py hookrelay-rootfs.tar
docker run --rm --entrypoint /app/.venv/bin/python hookrelay:ci -c "import sys, django, psycopg, uvloop, httptools; print(sys.version_info[:3], sys.executable)"
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy -v ${PWD}:/out aquasec/trivy:0.74.0 image --format cyclonedx --output /out/sbom-image.cdx.json hookrelay:ci
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy aquasec/trivy:0.74.0 image --scanners vuln,secret --pkg-types os,library --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
```

The scanner runs as the Dockerized `aquasec/trivy:0.74.0` (no host install), the same engine version CI pins. The CLI flag is `--pkg-types`; the pinned GitHub action still calls the same setting `vuln-type` and maps it internally — both are correct in their place. `sbom-image.cdx.json` and `hookrelay-rootfs.tar` are local evidence, not repository content. The runtime has no shell, so inspection happens from the host on the exported rootfs; `scripts/inspect_rootfs.py` fails on any shell, build tool, package manager, cache, test/doc content, dev package or setuid/setgid file.

### Forwarded-header trust

Uvicorn honours `X-Forwarded-*` only from `FORWARDED_ALLOW_IPS` (its own variable; default `127.0.0.1`; CIDR accepted). No wildcard exists in the image or `fly.toml`. CI proves both directions on the bridge network: from an untrusted source the header is ignored and Django answers 301 (it saw http); from an allowed subnet it is honoured and `/readyz` answers 200.

Production is different and remains OPEN: Fly documents that requests reach a Machine through Fly Proxy and documents the forwarded headers, but it does not publish a stable proxy-source CIDR, and one observed source address is not a boundary. Rule: **no production deployment until the trusted source range is established from a documented Fly property or a staged deployment proof that covers the actual routing topology**, recorded in DECISIONS.md. Never infer a CIDR from one request; never use `*`; if a stable safe allowlist cannot be established, stop for an explicit architecture decision rather than relaxing the gate. The loopback placeholder fails closed behind a proxy (every request redirects to https), which is the intended behaviour until that decision exists.

## Deploy

The image is built by the Dockerfile (bun stage for assets, uv stage for Python, `collectstatic` at build). Fly runs `web` (uvicorn) and `worker` (`db_worker`) process groups, `migrate` as the release command, and serves `/static/` straight from the image via `[[statics]]`. Secrets: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `ALLOWED_HOSTS`.
