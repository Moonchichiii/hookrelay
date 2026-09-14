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

## GitHub run on root commit fbae421 → v1.5 (container and toolchain)

| Finding | Class | Resolution |
|---|---|---|
| `security / image` red: 46 fixable Debian HIGH/CRITICAL in `python:3.14.4-slim`; 2 HIGH in `/usr/bin/uv` and `/usr/bin/uvx`; uv cache in the image | BLOCKER (real gate failure, nothing suppressed) | three-stage image; uv/uvx/Bun/caches/dev deps never in the runtime; base `python:3.14.7-slim-trixie` built and scanned as-is, no apt mutation; digest pin after a clean scan (v1.5) |
| Python drifted: Docker 3.14.4, CI "3.14", local 3.14.6, upstream 3.14.7 | design | `.python-version` = 3.14.7 as the single source; CI omits the input; Docker `ARG PYTHON_IMAGE` from the file; interpreter test locally and in the image (v1.5) |
| uv 0.11.7 → 0.12.13 | design | verified: `uv lock --check` unchanged, 3.14.7 installable, `uv audit --all-groups` no longer valid → command corrected (v1.5) |
| Trivy `ignore-unfixed` | design | removed; vuln + secret; image SBOM; unfixed = red until VEX (v1.5) |
| `--forwarded-allow-ips=*` inherited without justification | security decision | `FORWARDED_ALLOW_IPS` from the environment, default loopback; both directions proven in CI; Fly value measured at first deploy (v1.5) |
| SUID/SGID only printed | design | fail-closed allowlist gate, list measured by the owner (v1.5) |
| `typecheck:tools` not in CI | gap | blocking step in `ci / test` before the build (v1.5) |
| `.env.example` removed while README referenced it | gap | restored, sanitized, ports 55433/56380 (v1.5) |
| `apt-get upgrade` and system-pip removal proposed by the implementer | rejected by review | not done: mutable mirror is not reproducible; pip removal only for a proven reason (v1.5) |

## Static review of the v1.5 zip (01d684f6…) → v1.5.1

| Finding | Class | Resolution |
|---|---|---|
| CI `--build-arg PYTHON_IMAGE=…` would override a future digest pin in the Dockerfile | BLOCKER (latent) | build-arg removed from both workflows and the README; Dockerfile owns the reference; test pins its version to `.python-version` incl. `@sha256` (v1.5.1) |
| trivy-action v0.36.0 embeds Trivy 0.70.0 | design | `version: v0.74.0` on both invocations (v1.5.1) |
| `docs/security/README.md` still said unfixed findings are excluded | policy contradiction | rewritten to Decision 27 (v1.5.1) |
| PROOFS overclaimed "read-only token" and "images pinned" | wording | split into precise rows; digests GATE DEFINED (v1.5.1) |
| SBOM generated after the fail-closed scan | ordering | SBOM + upload before the scan (v1.5.1) |
| Fly trust range "measured from one request" | security procedure | production deploy blocked until a documented or staged-deployment-proven boundary exists (v1.5.1) |
| GitHub secret scanning: HIGH "PostgreSQL credentials" on a parser fixture in `tests/integration/test_settings.py` (host.example.test) | false positive, structural fix | all fixture DSNs assembled at runtime (`test_settings.py`, `test_skeleton.py`), decoded password built at runtime, repository hygiene gate added with a planted-literal negative check; incident to be resolved as test fixture after push (v1.5.1) |

## Owner's local image proof → v1.5.2 (runtime family selection)

| Finding | Class | Resolution |
|---|---|---|
| `python:3.14.7-slim-trixie` unmodified: 53 HIGH + 3 CRITICAL OS findings under the fail-closed policy | runtime rejected | Debian runtime dropped (v1.5.2) |
| Alpine reaches zero only with OS mutation plus pip removal (pip's vendored BOM as scanner noise) | rejected: mutation contradicts DECISION 25 | not adopted (v1.5.2) |
| Chainguard `python:latest-dev` (3.14.7, glibc) → `python:latest` (65532, minimal): Trivy 0/0 for OS and Python packages with the locked Hookrelay venv transferred and django/psycopg/uvloop/httptools importing | runtime selected | four-stage Dockerfile, digest-pinned inputs, shell-less host-side inspection, zero-SUID invariant, version/digest static tests (v1.5.2) |
| `Dockerfile.chainguard-test` was local experimentation | evidence only | not committed (v1.5.2) |
| Hygiene gate exempted loopback hosts broadly | tightening | explicit reviewed fixture combinations in approved contexts; loopback secret negative test (v1.5.2) |
| README/PROOFS wording: "read-only token", "same as CI", Docker rows PROVEN for a runtime no longer used, ruleset implied | precision | corrected; ruleset marked OPEN owner action (v1.5.2) |

## Static review of the 1644 and 1655 v1.5.2 zips → revision 2

| Finding | Class | Resolution |
|---|---|---|
| Inspector skipped non-regular entries before the forbidden-path check: `/bin/sh -> /bin/busybox` passed as "no shell" | BLOCKER (security gate bypass) | forbidden paths checked for every entry type; pip/pip3 and venv uv/uvx added (1655) |
| Inspector skipped directories before the tree check and matched trailing-slash prefixes only: an empty `/app/tests`, or `/app/tests`, `/app/docs`, `/app/node_modules`, `/root/.cache` as symlinks, passed as clean | BLOCKER (security gate bypass) | tree roots without trailing slash, root itself and everything beneath rejected for every entry type before the directory skip; fourteen-case synthetic regression (revision 2) |
| Decisions 18/20/32 contradicted 27/38/37 while all LOCKED | governance | statuses set to superseded/amended (1655) |
| Local wall expected 200 for a plain http `/livez` under `SECURE_SSL_REDIRECT`; deploy check missing; host Trivy assumed | precision | 301, deploy check with generated key, Dockerized `aquasec/trivy:0.74.0` (1655) |
| `fly.toml` commands relied on PATH in a shell-less image | hardening | absolute executables (1655) |
