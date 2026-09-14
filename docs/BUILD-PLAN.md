# HOOKRELAY — Build plan

Version 1.0 · 2026-09-13 · Status: LOCKED

## 0. Locked decisions

See `DECISIONS.md` for the dated log. In short: Django tasks framework (django-tasks-db) for delivery, hand-rolled SKIP LOCKED worker only as a D08 benchmark; Redis pub/sub for the live stream, LISTEN/NOTIFY only as a D08 benchmark; partitioning decided by measurement in D07; DRF is the product API, GraphQL is the D06 comparison; D09 Kafka and D10 RAG are optional labs the roadmap may stop before; bigint PK + UUIDv7 `public_id`; strict self-only CSP from D00; deny-by-default DRF; API keys hashed, signing secrets encrypted at rest; dependencies enter at first use; async only for SSE; per-app tests plus root cross-cutting tests with fast / concurrency / e2e lanes; every claim is a row in `PROOFS.md`; every drop goes förspec → build → evidence → GitHub-green → CLOSED, delivered as a complete canon zip with a machine diff.

## 1. Data model (end state after D04)

- **Tenant** — `public_id`, `name`, `slug`.
- **Membership** — `user`, `tenant`, `role ∈ {owner, viewer}`; unique (user, tenant).
- **ApiKey** — `tenant`, `prefix` (unique), `key_hash`, `scopes` (ArrayField), `revoked_at`, `last_used_at` (write-coalesced ≤ 1/min).
- **Endpoint** — `tenant`, `public_id`, `url`, `signing_secret` (encrypted, `kid$ciphertext`), `event_types` (empty = all), `status ∈ {active, paused, disabled}`, `consecutive_failures`, `circuit_open_until`, `version`.
- **Event** — `tenant`, `public_id`, `event_type`, `idempotency_key` (nullable), `payload` (JSON, capped), `received_at`; partial unique (tenant, idempotency_key).
- **Delivery** — `tenant`, `event`, `endpoint`, `public_id`, `state ∈ {pending, in_flight, succeeded, dead}`, `attempts`, `next_attempt_at`, `lease_until`, `last_error`, `replayed_from`, `finished_at`; partial index on `next_attempt_at WHERE state='pending'`; check `in_flight ⇒ lease_until IS NOT NULL`.
- **DeliveryAttempt** — `delivery`, `number`, `started_at`, `duration_ms`, `response_status`, `error_kind`, `response_excerpt` (≤ 1 KB), `signature_ts`; append-only; partition candidate.
- **AuditEntry** — `tenant`, actor, action, target, `diff`, `prev_hash`, `hash`, `created_at`; trigger rejects UPDATE/DELETE.

## 2. Drops

### D00 — Skeleton (v1.3 delivered)
Stack, settings split, custom user, strict CSP, `/livez` + `/readyz`, mypy strict, htmx 4 checker, Bun-native assets, hardened CI (hooks, checks, deploy check, fresh migrate, coverage floor, warnings as errors, hash-verified audits, bun audit, SBOM, Docker smoke, Trivy, SHA-pinned actions), CodeQL, Docker, Fly, compose, PROOFS.

### D01 — Accounts, tenancy, API keys
Tenant, Membership, ApiKey; `create_api_key` (plaintext once), `revoke_api_key`; `ApiKeyAuthentication` (prefix lookup, hash compare, revoked = fail), `HasScope`, `IsTenantMember`; throttle keyed by API key on Redis; `GET /api/me/`, `POST/GET/DELETE /api/keys/`. Tests: valid, revoked, wrong secret, missing scope, other tenant → 404, throttle shared across clients, `last_used_at` coalesced, hash-only storage. Dependencies: none new.

### D02 — Endpoints, publish, transactional outbox, audit chain
Endpoint, Event, Delivery, AuditEntry. `publish_event` in one transaction (idempotency via the DB index, fan-out with `bulk_create`). Endpoint ModelViewSet with `If-Match`/ETag → 412; https-only + creation-time SSRF (`ssrf.py`). Event publish as `APIView` + `Serializer`, `Idempotency-Key`, 201/200. Signing secrets encrypted (`cryptography`, key-id rotation). Audit hash chain, trigger via `RunSQL`, `verify_audit_chain`. Tests: idempotency race → one Event; fan-out rollback; paused endpoint excluded; audit immutability and tamper detection; encryption; creation-time SSRF matrix; 412; oversized payload. Dependencies: cryptography.

### D03 — Delivery via the tasks framework, failure-injection receiver, delivery-time SSRF
`deliver(delivery_id, attempt)` task: `select_for_update` guard, lease, httpx sync POST with `X-Hookrelay-Id/Timestamp/Signature`, timeouts, capped body, no redirects, TLS verified, validated-IP transport preserving Host/SNI; result transaction (succeeded / pending + backoff + jitter + `run_after` re-enqueue / dead after 8). `publish_event` enqueues in-transaction. `requeue_stuck` periodic job. `scripts/receiver.py` failure-injection ASGI app. Tests: respx unit; duplicate execution → one call; two `db_worker` processes → each delivery once; lease recovery; delivery-time SSRF; receiver system tests. CI: concurrency lane job. Dependencies: httpx; dev respx, time-machine.

### D04 — Circuit breaker, replay, DLQ, filtering, pagination, OpenAPI
Circuit state under `select_for_update`, half-open probe, `F()` counters; pause/resume; replay single and bulk (audited, 409 on pending/in_flight); Delivery `ReadOnlyModelViewSet` with django-filter; `CursorPagination` on attempts; uniform error contract; complete schema. Dependencies: django-filter.

### D05 — SSE over Redis and the HTMX UI
`on_commit` → `PUBLISH tenant:<id>:deliveries`; async SSE view with redis-py PubSub, heartbeat, `Last-Event-ID` gap fill; dashboard, delivery detail, dead-letter page with replay, endpoint pages; Alpine for local state. Tests: event received; gap fill; tenant isolation on the stream; HTMX POST with CSRF; browser proofs (Playwright decision at förspec).

### D06 — GraphQL
strawberry-django; queries and mutations through the D02–D04 services; session + API key context; tenant base queryset; depth and complexity limits; introspection off in prod; optimizer. Tests: query count independent of result size; limits; cross-tenant leakage suite over REST + GraphQL + SSE + HTMX; mutation permission parity. Dependencies: strawberry-graphql-django.

### D07 — Performance and the partitioning decision
k6 (ingest and delivery throughput with 1/2/4 workers), `pg_stat_statements`, `explain()` assertions, DeliveryAttempt at 1M/5M rows, retention cost; decision recorded; if partitioning wins: `CompositePrimaryKey`, `RunSQL` partitioning, maintenance and retention as the first Django Tasks maintenance jobs; pool measured. Results in README.

### D08 — Chaos and architecture alternatives
10k deliveries, 8 workers, random SIGKILL, hostile receiver; invariants: no lost delivery, no simultaneous lease, leases recover, valid terminal states, audit chain valid. Alternative A: hand-rolled SKIP LOCKED worker benchmarked against django-tasks-db. Alternative B: LISTEN/NOTIFY stream transport benchmarked against Redis (local only).

### D09 — Kafka event-backbone lab (local only)
Single-node broker in compose; `OutboxMessage` in `publish_event`'s transaction; SKIP LOCKED relay; topic keyed by `endpoint_id`; shadow consumer + second group; `ProcessedMessage` unique `(event_id, consumer)`. Proofs: no loss across relay kill; per-endpoint ordering; consumer crash without duplicate effect; throughput vs consumers; partition-key skew. Optional dependency group `kafka`.

### D10 — RAG operations assistant
`pgvector/pgvector:pg17`; Document / DocumentVersion / Chunk; ingestion as a Django Task with atomic version swap; hybrid retrieval (FTS + cosine, RRF); tenant-scoped ANN with a measured strategy; `POST /api/assistant/query/` returning answer + sources + live ORM evidence; read-only model with no tools; approved docs only; evaluation set with recorded embedding fixtures in CI. Optional dependency group `rag`.

## 3. Open items carried into förspecs
D01: `readyz` dead-server approach if any. D03: transport pinning design; jitter formula. D05: htmx 4 SSE mechanism; Playwright yes/no. D06: strawberry-django compatibility. D07: pool on/off. D09: client library. D10: embedding model and chunking defaults.
