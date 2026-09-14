# Förspec D02 — Endpoints, publish, transactional outbox, audit chain

Version 0.1 · Status: DRAFT (design freeze happens when D02 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Endpoints, publish, transactional outbox, audit chain, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/ingest, apps/delivery, apps/audit

## Dependencies added in this drop
cryptography

## Scope
Endpoint, Event, Delivery, AuditEntry; publish_event (idempotent, fan-out in one transaction); Endpoint ModelViewSet with If-Match; POST /api/events/ as APIView + Serializer; ssrf.py creation-time checks; secrets.py (encrypt/decrypt, key-id rotation); audit hash chain + trigger migration + verify_audit_chain command.

## Tests and negative tests
idempotency race → one Event; fan-out rollback; paused endpoint excluded; audit UPDATE/DELETE rejected; chain verifies and tamper detected; secret encrypted at rest; SSRF creation matrix; stale If-Match → 412; oversized payload rejected.

## PROOFS rows moved to PROVEN
idempotent publish; atomic fan-out; audit immutability; secrets encrypted; creation-time SSRF.

## Open items to decide at design freeze
canonical JSON for the hash chain; payload size cap; event_type validation rules.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
