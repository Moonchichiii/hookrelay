# Förspec D07 — Performance and the partitioning decision

Version 0.1 · Status: DRAFT (design freeze happens when D07 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Performance and the partitioning decision, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
scripts/k6, apps/delivery, docs

## Dependencies added in this drop
none (k6 external)

## Scope
k6 scripts; pg_stat_statements; explain() assertions for hot paths; DeliveryAttempt at 1M/5M rows; retention cost; partitioning decision; if yes: CompositePrimaryKey + RunSQL partitioning + maintenance and retention as the first Django Tasks maintenance jobs; pool measured; results table.

## Tests and negative tests
query budgets for hot paths; before/after numbers; contract tests identical before and after any optimisation.

## PROOFS rows moved to PROVEN
partitioning decision with numbers; retention cost; query budgets.

## Open items to decide at design freeze
pool on/off; retention period.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
