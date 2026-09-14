# Förspec D04 — Circuit breaker, replay, DLQ, filtering, pagination, OpenAPI

Version 0.1 · Status: DRAFT (design freeze happens when D04 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Circuit breaker, replay, DLQ, filtering, pagination, OpenAPI, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/delivery

## Dependencies added in this drop
django-filter

## Scope
circuit state transitions under select_for_update with F() counters; half-open probe; pause/resume; replay single and bulk with audit; Delivery ReadOnlyModelViewSet with filters; CursorPagination on attempts; uniform error contract via exception handler; complete OpenAPI.

## Tests and negative tests
concurrent failures open the circuit once; half-open closes on success; paused receives nothing; replay pending → 409; viewer cannot replay; bulk replay audited; cursor stable under inserts; schema validates.

## PROOFS rows moved to PROVEN
circuit correct under concurrency; replay permissions; stable pagination.

## Open items to decide at design freeze
threshold and cooldown values; replay from succeeded allowed or not.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
