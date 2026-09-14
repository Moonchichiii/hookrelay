# Förspec D06 — GraphQL

Version 0.1 · Status: DRAFT (design freeze happens when D06 starts; FILES TO TOUCH becomes authoritative then)

## Goal
GraphQL, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/graphql

## Dependencies added in this drop
strawberry-graphql-django

## Scope
schema over event/events/endpoint(s)/delivery(s)/attempts; mutations replayDelivery, pauseEndpoint, createEndpoint through services; session + API key context; tenant base queryset; depth and complexity limits; introspection off in prod; optimizer.

## Tests and negative tests
query count identical for 1 and 50 deliveries; limits enforced; cross-tenant leakage suite over four surfaces; mutation permission parity with REST.

## PROOFS rows moved to PROVEN
N+1 bounded; leakage zero; limits enforced.

## Open items to decide at design freeze
strawberry-django compatibility with 3.14 / 6.1; auth context design.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
