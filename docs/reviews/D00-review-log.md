# D00 review log

Every finding against the D00 skeleton, its classification, and where it was resolved.

## Found during the v1.1 build (self-review)

| Finding | Class | Resolution |
|---|---|---|
| uvicorn missing from the dependency list although §5/§6b/§11 required it | BLOCKER | added `uvicorn[standard]` (v1.1) |
| Static files 404 under uvicorn (Django serves them only via runserver) | BLOCKER | `staticfiles_urlpatterns()` under DEBUG; Fly `[[statics]]` in production (v1.1) |
| POST /healthz gave 403 live but 405 in tests (test client skips CSRF) | BLOCKER | probes are `csrf_exempt` + `require_GET`, contract identical everywhere (v1.1) |

## Static review of the 1453 zip → v1.2

| Finding | Class | Resolution |
|---|---|---|
| No custom user model before the first migration | BLOCKER | `accounts.User(AbstractUser)`, `AUTH_USER_MODEL` (v1.2) |
| `hx-headers` on body does not reach descendants in htmx 4 | BLOCKER | `hx-headers:inherited` (v1.2); verified with htmx's own upgrade checker |
| `htmx.config.selfRequestsOnly` removed in htmx 4 | BLOCKER | deleted; htmx 4 defaults to same-origin (v1.2) |
| CSP deferred to a later drop | design | strict self-only CSP from D00, header test (v1.2) |
| No static typing gate | design | mypy strict + django-stubs + DRF stubs (verified against the exact lock) (v1.2) |
| pip-audit and pre-commit run via `uvx`, not locked | design | both in the dev group, run with `uv run` (v1.2) |
| No htmx upgrade checker in CI | design | `bun run htmx:check` gate, verified to exit 1 on bad input (v1.2) |
| Single `/healthz` mixed liveness and readiness | design | `/livez` (zero queries) + `/readyz` (bounded probes) (v1.2) |
| `testpaths` did not include per-app tests | design | `testpaths = ["apps", "tests"]` (v1.2) |
| `build:js` used `mkdir -p`/`cp` (unverified on Windows) | design | `scripts/copy-assets.ts`, Bun-native (v1.2) |
| Future-only dependencies in D00 | design | django-filter, httpx, factory-boy, respx, time-machine removed until first use (v1.2) |
| No proof registry | design | `docs/PROOFS.md` (v1.2) |
| pre-commit handed the generated migration to ruff past the exclude | found in v1.2 gate run | `--force-exclude` on both ruff hooks (v1.2) |

## Static review of the 1525 zip → v1.3

| Finding | Class | Resolution |
|---|---|---|
| `database_from_url` let a URL parameter override the enforced `connect_timeout` | BLOCKER | applied last; pinned by test (v1.3) |
| Audit export dropped artifact hashes | correction | `pip-audit --strict --require-hashes` on production and all-groups exports (v1.3) |
| Coverage collected but not enforced | design | branch coverage, floor 95%, measured 100% (v1.3) |
| Warnings could accumulate silently | design | `filterwarnings = ["error"]`, zero exclusions (v1.3) |
| `manage.py check`, `check --deploy`, fresh migrate, pre-commit not in CI | design | all four in the `test` job; deploy check at WARNING level with `SECURE_HSTS_PRELOAD` (v1.3) |
| Production fail-closed only observed manually | design | parametrised in-process tests, PROVEN (v1.3) |
| No PostgreSQL readiness-failure test | design | probe-failure test with log/response separation; lossy-cache test (v1.3) |
| CSP test did not assert the whole policy | design | exact policy dictionary (v1.3) |
| Autouse fixture made every test depend on Redis | design | opt-in `redis_cache` (v1.3) |
| `tmp_path: object` with a `type: ignore` | hygiene | `tmp_path: Path` (v1.3) |
| No frontend audit, no SBOM, no container test or scan | design | `bun audit`, CycloneDX artifact, Docker migrate/boot/probe, Trivy (v1.3) |
| Actions referenced by moving tags; broad token | design | full SHAs from `git ls-remote`, `contents: read` (v1.3) |
| No branch protection | operational | ruleset checklist in README; configured by the owner in GitHub |

## Audit of the three copy-in zips → v1.4 (supply chain only)

| Finding | Class | Resolution |
|---|---|---|
| `--frozen` accepts a lock that no longer matches `pyproject.toml` | P0 | demonstrated in the sandbox (`--frozen` exit 0, `--locked` exit 1 on a stale manifest); `uv lock --check`, `--locked` everywhere, `UV_LOCKED=1` (v1.4) |
| Audits ran only on code changes | design | `security.yml` on PR, push, daily schedule and dispatch; Trivy moved there; Dependabot config; dependency review on PRs (v1.4) |
| uv, bun and base images floated on moving tags | design | exact versions pinned; digests by owner command, then Dependabot (v1.4) |
| PROOFS claim wording conflated pip-audit (no ignores) with Trivy (`ignore-unfixed`) | wording | two separate, surgical rows (v1.4) |
| `uv audit` available as defence in depth | optional | non-blocking secondary step behind the preview flag (v1.4) |
