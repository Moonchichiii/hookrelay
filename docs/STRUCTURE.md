# Intended repository structure

Which drop creates each part. Empty directories are not tracked by git; create them when the drop that fills them starts.

```
hookrelay/
  config/                      D00   settings (base/dev/test/prod), asgi, wsgi, urls, project views (index, livez, readyz)
  apps/
    accounts/                  D00   User; D01 Tenant, Membership, ApiKey, authentication, permissions, throttling, api/
    ingest/                    D02   Event, publish_event service, POST /api/events/
    delivery/                  D02   Endpoint, Delivery, DeliveryAttempt, ssrf.py, secrets.py; D03 tasks.py, signing.py, transport.py; D04 circuit, replay, filters
    audit/                     D02   AuditEntry, hash chain, trigger migration, verify_audit_chain
    stream/                    D05   Redis publish, SSE views; D08 LISTEN/NOTIFY alternative
    ui/                        D05   HTMX views and templates
    graphql/                   D06   schema, types, resolvers, mutations
    outbox/                    D09   OutboxMessage, relay, consumers (lab)
    assistant/                 D10   Document, DocumentVersion, Chunk, ingestion, retrieval, query API (lab)
  scripts/                     D00   copy-assets.ts; D03 receiver.py; D07 k6/
  static/src/                  D00   app.css, app.js (dist is built, never committed)
  templates/                   D00   base.html, index.html; D05 pages
  tests/
    integration/               D00   skeleton and settings contracts
    concurrency/               D02   idempotency race; D03 worker and lease tests; D08 chaos
    system/                    D03   failure-injection receiver tests
    security/                  D02   SSRF creation matrix; D03 delivery matrix; D04+ tenant leakage suite
  docs/
    BUILD-PLAN.md  DECISIONS.md  PROOFS.md  STRUCTURE.md
    forspec/D00-skeleton.md … D10-rag.md
    LEVERANS-D00.md …
    reviews/
    security/                  exception policy and records
  .github/workflows/           ci.yml, codeql.yml
  Dockerfile  fly.toml  compose.yaml  pyproject.toml  uv.lock  package.json  bun.lock
```

Each app keeps the same shape: `models.py`, `services.py` (writes), `selectors.py` (reads), `api/` (serializers, views, urls), `tests/`. No utils folders; no abstraction before a concrete need.
