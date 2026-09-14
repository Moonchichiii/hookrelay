# Förspec D01 — Accounts, tenancy, API keys

Version 0.1 · Status: DRAFT (design freeze happens when D01 starts; FILES TO TOUCH becomes authoritative then)

## Goal
Accounts, tenancy, API keys, as specified in BUILD-PLAN v1.0 §2.

## Areas touched
apps/accounts

## Dependencies added in this drop
none

## Scope
Tenant, Membership, ApiKey models and migration; services create_api_key / revoke_api_key; selectors; ApiKeyAuthentication, HasScope, IsTenantMember; API-key throttle on Redis; GET /api/me/, POST/GET/DELETE /api/keys/; django.contrib.postgres in INSTALLED_APPS; BUILD-PLAN and PROOFS PLANNED rows committed.

## Tests and negative tests
valid key authenticates; revoked never; wrong secret with valid prefix; missing scope → 403; other tenant's key → 404; throttle → 429 shared across two clients; last_used_at write-coalesced; DB holds hash only.

## PROOFS rows moved to PROVEN
keys stored one-way; revocation immediate; throttling cross-process; tenant scoping on lists.

## Open items to decide at design freeze
readyz dead-server approach if a supported one exists.

## Gates
Same as every drop: read-only intake against the closed previous drop, förspec locked, build, evidence (sandbox / Mats / GitHub tiers), LEVERANS with BEVISAR / BEVISAR INTE and machine diff, GitHub-green (all required checks, CodeQL delta 0), CLOSED.
