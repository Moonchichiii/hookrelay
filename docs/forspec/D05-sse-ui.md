# Förspec D05 — SSE over Redis and the HTMX UI

Version 0.1 · Status: DRAFT (design freeze happens when D05 starts; FILES TO TOUCH becomes authoritative then)

## Goal
SSE over Redis and the HTMX UI, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/stream, apps/ui, templates

## Dependencies added in this drop
none (Playwright as dev dependency is a decision here)

## Scope
on_commit Redis publish; async SSE view with PubSub, heartbeat, Last-Event-ID gap fill; dashboard, delivery detail, dead-letter page with replay, endpoint pages; Alpine for local state.

## Tests and negative tests
event received after attempt; gap fill on reconnect; tenant B never sees tenant A; HTMX POST with CSRF succeeds; browser proofs for htmx under CSP and SSE row.

## PROOFS rows moved to PROVEN
SSE tenant isolation; gap fill; htmx under CSP in a browser.

## Open items to decide at design freeze
htmx 4 SSE mechanism; Playwright yes/no; per-client vs shared subscription.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
