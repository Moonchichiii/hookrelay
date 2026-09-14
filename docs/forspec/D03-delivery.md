# Förspec D03 — Delivery via the tasks framework, receiver, delivery-time SSRF

Version 0.1 · Status: DRAFT (design freeze happens when D03 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Delivery via the tasks framework, receiver, delivery-time SSRF, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/delivery, scripts/receiver.py, tests/concurrency, tests/system, tests/security

## Dependencies added in this drop
httpx; dev: respx, time-machine

## Scope
deliver task with select_for_update guard and lease; signing.py; transport.py with validated-IP connection; backoff with jitter and run_after re-enqueue; dead after 8; publish_event enqueues in-transaction; requeue_stuck periodic job; failure-injection receiver; CI concurrency lane job.

## Tests and negative tests
respx: 2xx / 5xx / timeout / last failure; signature verifiable; duplicate execution → one HTTP call; two db_worker processes → each delivery once; lease recovery; DNS-to-private blocked; redirect not followed; receiver fail-next-3, sleep, huge.

## PROOFS rows moved to PROVEN
signed deliveries verifiable; at-least-once with idempotent guard; no double attempt; lease recovery; delivery-time SSRF.

## Open items to decide at design freeze
transport pinning design (custom httpx transport vs resolver hook); jitter formula; lease length.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
