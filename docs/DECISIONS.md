# Decision log

Locked decisions, in the order they were taken. A locked decision is not reopened by "I would have done it differently"; it changes only by an explicit new decision recorded here.

| # | Date | Decision | Status |
|---|---|---|---|
| 1 | 2026-09-13 | Stack: Python 3.14, Django 6.1, DRF 3.18, PostgreSQL 17 (Neon), Redis 7 (Upstash), django-htmx + htmx 4, Alpine CSP build, Tailwind 4, uv, bun, uvicorn, Fly.io | LOCKED |
| 2 | 2026-09-13 | Project: webhook delivery service ("hookrelay"), small domain, deep backend | LOCKED |
| 3 | 2026-09-13 | Delivery engine: Django tasks framework with django-tasks-db. Reaffirmed three times against advice to hand-roll; the hand-rolled SKIP LOCKED loop is built in D08 as a benchmarked alternative | LOCKED |
| 4 | 2026-09-13 | Live stream: Redis pub/sub in production; PostgreSQL LISTEN/NOTIFY in D08 as a benchmarked alternative (Neon: unsupported over the pooled endpoint, listeners lost on scale-to-zero) | LOCKED |
| 5 | 2026-09-13 | Partition DeliveryAttempt only after measurement (D07) | LOCKED |
| 6 | 2026-09-13 | Ids: bigint PK + UUIDv7 `public_id`; httpx sync for delivery; async only for SSE views | LOCKED |
| 7 | 2026-09-13 | Dockerfile + fly.toml ship in D00; local Postgres and Redis via Docker (`compose.yaml`) | LOCKED |
| 8 | 2026-09-13 | GraphQL as D06 (queries + mutations only, same services, N+1 proof); performance D07; chaos D08 | LOCKED |
| 9 | 2026-09-13 | Custom `accounts.User(AbstractUser)` before the first migration; application code uses `get_user_model()` only | LOCKED |
| 10 | 2026-09-13 | Strict self-only CSP from D00; no nonce until an inline requirement is proven; no DRF browsable API | LOCKED |
| 11 | 2026-09-13 | A dependency enters `uv.lock` in the drop whose code or tests first use it; lab dependencies in optional groups | LOCKED |
| 12 | 2026-09-13 | Tests: `apps/<app>/tests/` + `tests/{integration,concurrency,system,security}/`, `testpaths = ["apps", "tests"]`; fast / concurrency / e2e lanes | LOCKED |
| 13 | 2026-09-13 | django-tasks-db, `TASKS` and the `worker` process stay in D00 (topology fixed) | LOCKED |
| 14 | 2026-09-13 | Signing secrets encrypted at rest with the key outside the DB and key-id rotation (D02); API keys hashed | LOCKED |
| 15 | 2026-09-13 | `docs/PROOFS.md` claim → evidence registry maintained every drop | LOCKED |
| 16 | 2026-09-13 | D09 Kafka event-backbone lab, local only; D10 RAG operations assistant; both optional add-ons | LOCKED |
| 17 | 2026-09-13 | BUILD-PLAN v1.0 | LOCKED |
| 18 | 2026-09-14 | Container scan: Trivy, CRITICAL/HIGH, `ignore-unfixed`, required | LOCKED |
| 19 | 2026-09-14 | `SECURE_HSTS_PRELOAD = True` as a header flag so the deploy checklist passes at WARNING level with nothing silenced | LOCKED |
| 20 | 2026-09-14 | Every GitHub Action pinned to a full commit SHA; workflow token read-only; `main` protected by a ruleset requiring `test`, `security`, `docker`, `analyze (python)`, `analyze (javascript-typescript)` | LOCKED |
| 21 | 2026-09-14 | No gate ever moves backward for new code; ignores are narrow and reasoned; warnings are errors; no CI retries for flaky tests; vulnerability exceptions need a dated record | LOCKED |
| 22 | 2026-09-14 | Lock discipline: `uv lock --check` first, `--locked` (never `--frozen`) in CI, exports and the image; `UV_LOCKED=1` workflow-wide | LOCKED |
| 23 | 2026-09-14 | Supply-chain scanning is time-triggered as well as change-triggered (`security.yml` daily + dispatch); Dependabot for uv, bun, actions, docker, compose; dependency review on PRs at `low` | LOCKED |
| 24 | 2026-09-14 | Toolchain pinned to the versions that produced the evidence (uv 0.11.7, bun 1.4.2, python 3.14.4-slim, uv image 0.11.7); digests added by the owner, then maintained by Dependabot; `uv audit` is a non-blocking secondary signal while in preview | LOCKED |
