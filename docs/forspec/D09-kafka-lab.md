# Förspec D09 — Kafka event-backbone lab (local only)

Version 0.1 · Status: DRAFT (design freeze happens when D09 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Kafka event-backbone lab (local only), as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/outbox, compose.yaml

## Dependencies added in this drop
kafka client in optional group `kafka`

## Scope
single-node broker in compose; OutboxMessage in publish_event's transaction; SKIP LOCKED relay; topic keyed by endpoint_id; shadow consumer and a second group; ProcessedMessage unique (event_id, consumer).

## Tests and negative tests
no loss across relay kill; per-endpoint ordering with multiple partitions/consumers; consumer crash without duplicate effect; throughput vs 1/2/4/8 consumers; partition-key skew.

## PROOFS rows moved to PROVEN
five Kafka proofs.

## Open items to decide at design freeze
client library by 3.14 wheel availability; broker image.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
