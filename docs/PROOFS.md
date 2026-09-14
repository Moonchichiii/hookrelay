# Hookrelay proof registry

Every engineering claim the project makes is listed here with the evidence that backs it. A row is PROVEN only when the evidence exists in the repository and runs in CI. Claims without evidence are listed as PLANNED with the drop that will prove them.

| Claim | Evidence | Status |
|---|---|---|
| Custom user model selected before any domain migration | `apps/accounts/migrations/0001_initial.py`; `apps/accounts/tests/test_user_model.py` | PROVEN (D00) |
| `/livez` performs no database queries | `tests/integration/test_skeleton.py::test_livez_is_ok_without_touching_the_database` (`django_assert_num_queries(0)`) | PROVEN (D00) |
| `/readyz` performs a real PostgreSQL round-trip | `tests/integration/test_skeleton.py::test_readyz_reports_db_and_redis_ok` | PROVEN (D00) |
| `/readyz` performs a real Redis round-trip and degrades to 503 without leaking the location | `tests/integration/test_skeleton.py::test_readyz_degrades_when_redis_is_unreachable` | PROVEN (D00) |
| `/readyz` degrades to 503 when the PostgreSQL probe fails; detail goes to the log, never the response | `tests/integration/test_skeleton.py::test_readyz_degrades_when_the_database_probe_fails` | PROVEN (D00, probe-level; a dead server is not simulated) |
| `/readyz` treats a cache that loses writes as not ready | `tests/integration/test_skeleton.py::test_readyz_treats_a_cache_that_loses_writes_as_an_error` | PROVEN (D00) |
| CSP is exactly the intended strict self-only policy (no unsafe-inline, unsafe-eval or nonce) | `tests/integration/test_skeleton.py::test_csp_header_is_exactly_the_intended_policy` | PROVEN (D00) |
| Static files are served by Django only under DEBUG | `tests/integration/test_skeleton.py::test_static_files_are_served_by_django_only_in_debug` | PROVEN (D00) |
| A DATABASE_URL parameter cannot override the enforced connect timeout | `tests/integration/test_settings.py::test_database_url_cannot_override_the_enforced_connect_timeout` | PROVEN (D00) |
| Templates and JS contain no known htmx 2 → 4 migration issues | `bun run htmx:check` (CI gate; exits 1 on findings) | PROVEN (D00) |
| Every model change has a migration | `tests/integration/test_skeleton.py::test_no_migrations_are_missing` | PROVEN (D00) |
| The OpenAPI schema generates without warnings | `tests/integration/test_skeleton.py::test_schema_generates_without_warnings` | PROVEN (D00) |
| Production settings fail closed without each required value | `tests/integration/test_settings.py::test_production_settings_fail_closed_without_each_required_value` | PROVEN (D00) |
| Production settings are hardened when configured (DEBUG off, SSL redirect, secure cookies, HSTS, CSP, proxy header) | `tests/integration/test_settings.py::test_production_settings_are_hardened_when_fully_configured` | PROVEN (D00) |
| Production deploy checklist has no warnings | CI: `manage.py check --deploy --fail-level WARNING` | PROVEN (D00, CI gate) |
| The suite emits no Python warnings | pytest `filterwarnings = ["error"]`, zero exclusions | PROVEN (D00) |
| Branch coverage never drops below 95% | pytest `--cov-branch --cov-fail-under=95` | PROVEN (D00, CI gate) |
| `uv.lock` matches `pyproject.toml`; nothing installs from a stale lock | CI: `uv lock --check`, `UV_LOCKED=1`, `uv sync --locked` (a stale manifest was shown to fail with `--locked` and pass with `--frozen`) | PROVEN (D00, CI gate) |
| No known vulnerability reported by pip-audit in either the production or the full resolved Python dependency set at scan time; requirements fully pinned and hash-bearing; no ignores | `security.yml`: `pip-audit --strict --require-hashes` on both `--locked` exports | PROVEN (D00, CI gate) |
| No known vulnerability reported by `bun audit` in the locked frontend set at scan time | `security.yml`: `bun audit` | PROVEN (D00, CI gate) |
| A vulnerability disclosed after a merge is detected without a code change | `security.yml` daily schedule; Dependabot alerts (repository setting) | PROVEN (D00, CI gate) once the schedule has run |
| A dependency change that introduces a known vulnerability cannot be merged | `security.yml` job `dependency-review` (`fail-on-severity: low`) | PROVEN (D00, CI gate) on a public repository with the dependency graph enabled |
| The final image migrates, boots and answers `/livez` and `/readyz` through the proxy contract | `ci.yml` job `docker` | GATE DEFINED (D00 v1.5.2); PROVEN by a green run |
| Zero known unsuppressed CRITICAL/HIGH findings (vuln + secret, OS + library) in the final runtime image at scan time; no ignore-unfixed, no ignore file, no soft-fail | `security.yml` job `image`, daily | GATE DEFINED (D00 v1.5.2); PROVEN only by a green scan of the exact built image (the owner's local Chainguard proof image scanned 0/0 under the same policy) |
| The final runtime rootfs has no shell, build tooling, package manager, caches, tests/docs/.env or dev packages, and zero setuid/setgid files; runs as 65532 | `scripts/inspect_rootfs.py` via `ci.yml` job `docker` (self-tested on synthetic rootfs tars) | GATE DEFINED (D00 v1.5.2); PROVEN by a green run of the Chainguard image |
| `.python-version` is exactly 3.14.7 and the local suite runs on it | `tests/integration/test_toolchain.py` | PROVEN (D00) |
| The final image executes Python 3.14.7 from `/app/.venv` and imports django, psycopg, uvloop, httptools | `ci.yml` job `docker` | GATE DEFINED (D00 v1.5.2); PROVEN by a green run (owner's local proof image showed the same, see LEVERANS) |
| `X-Forwarded-Proto` is ignored from untrusted sources and honoured from `FORWARDED_ALLOW_IPS` | `ci.yml` job `docker` (bridge-network probe both ways) | GATE DEFINED (D00); PROVEN by a green run |
| Production forwarded-header trust is a stable, documented or staged-deployment-proven boundary, never inferred from one request and never `*` | DECISIONS 29; production deploy blocked until established | OPEN — deploy blocked |
| Every GitHub Action is pinned to an immutable commit SHA; workflow token permissions default to `contents: read`, with CodeQL alone receiving the scoped `security-events: write` it requires | `.github/workflows/*.yml` | PROVEN (D00) |
| uv 0.12.13, bun 1.4.2 and Python 3.14.7 are pinned by exact version | `.python-version`, `Dockerfile`, workflows, `tests/integration/test_toolchain.py` | PROVEN (D00) |
| `main` is protected by a ruleset requiring the seven checks | GitHub configuration | OPEN — owner action, not yet configured |
| No unapproved credential-bearing URI literal exists in the tree: only explicit reviewed synthetic/local fixtures in approved contexts; loopback alone is no exemption | `tests/security/test_repository_hygiene.py` (gate + negative self-test incl. a loopback secret) | PROVEN (D00) |
| Every repository-owned image reference is an immutable index digest (syntax and presence enforced) | `tests/security/test_image_references.py`; `Dockerfile`, `compose.yaml`, `ci.yml` | STATIC PROVEN (D00 v1.5.2); digest pinning PROVEN when this exact tree builds and passes the image gates |
| Publishing is idempotent under concurrent identical requests | concurrency test | PLANNED (D02) |
| Fan-out and audit entries commit atomically with the event | transaction test | PLANNED (D02) |
| Audit chain rejects UPDATE/DELETE and verifies end to end | trigger + verify command test | PLANNED (D02) |
| Duplicate execution of a delivery task never produces two HTTP calls | concurrency test | PLANNED (D03) |
| Two workers over one backlog attempt every delivery exactly once | multi-process test | PLANNED (D03) |
| Stuck in-flight deliveries are requeued after the lease expires | crash test | PLANNED (D03) |
| Hostile URLs never produce an internal connection (creation and delivery time) | SSRF matrix | PLANNED (D03) |
| Cross-tenant isolation across REST, HTMX, SSE and GraphQL | leakage suite | PLANNED (D04–D06) |
| GraphQL query count is independent of result size | bounded-query test | PLANNED (D06) |
| Partitioning DeliveryAttempt is worth it | before/after benchmark | PLANNED (D07) |
| No lost delivery under random worker death and endpoint failure | chaos test | PLANNED (D08) |
