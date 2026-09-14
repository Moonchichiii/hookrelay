# Förspec D08 — Chaos and architecture alternatives

Version 0.1 · Status: DRAFT (design freeze happens when D08 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Chaos and architecture alternatives, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
tests/concurrency, apps/delivery, apps/stream

## Dependencies added in this drop
none

## Scope
chaos test (10k deliveries, 8 workers, random SIGKILL, hostile receiver) with invariants; hand-rolled SKIP LOCKED run_worker behind the delivery contract benchmarked against django-tasks-db; LISTEN/NOTIFY transport behind the stream interface benchmarked against Redis (local only).

## Tests and negative tests
no lost delivery; no simultaneous lease; leases recover; valid terminal states; audit chain valid; both comparisons with numbers.

## PROOFS rows moved to PROVEN
chaos invariants; two comparisons.

## Open items to decide at design freeze
kill strategy; run length; comparison metrics.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
