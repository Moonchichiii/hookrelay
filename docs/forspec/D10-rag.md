# Förspec D10 — RAG operations assistant

Version 0.1 · Status: DRAFT (design freeze happens when D10 starts; FILES TO TOUCH becomes authoritative then)

## Goal
RAG operations assistant, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/assistant, compose.yaml, .github/workflows/ci.yml

## Dependencies added in this drop
pgvector, openai in optional group `rag`

## Scope
pgvector image for local and CI, extension on Neon; Document / DocumentVersion / Chunk; ingestion task with atomic version swap; hybrid retrieval (FTS + cosine, RRF); tenant-scoped ANN with a measured strategy; POST /api/assistant/query/ with sources and live ORM evidence; read-only model with no tools; HTMX assistant page; evaluation set with recorded embedding fixtures.

## Tests and negative tests
zero cross-tenant retrieval with identical text; injected instructions cannot change data access; deleted documents vanish; re-index atomic; hybrid ≥ vector-only on the set; latency measured.

## PROOFS rows moved to PROVEN
RAG security and quality proofs.

## Open items to decide at design freeze
embedding model; chunking defaults; ANN filtering strategy.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
