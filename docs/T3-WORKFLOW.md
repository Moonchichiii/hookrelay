# Hookrelay T3 workflow

Status: owner-approved operating policy, 2026-09-19.
Applies to all tasks. D00 is the manually controlled bootstrap; D01 onward uses
the architect/build/review loop. The current roadmap defines D00-D10 only; this
policy does not invent or authorize D11-D12.

## 1. Intake and pre-build gate

Astra records exact branch, HEAD, base and its selection rationale, short Git
status, current drop/förspec version and LOCKED status, FILES TO TOUCH, blockers,
prior-drop closure evidence, migrations, neighboring tests and local service needs.
Read only the minimum authoritative material listed in AGENTS.md. Stop conditions
in AGENTS.md apply before any implementation, including remediation.

Build a task-specific risk map. For each dimension below record the concrete
invariant, abuse/failure case, mitigation and required evidence, or a reasoned N/A.
Do not turn this list into unrelated work.

| Dimensions | Review questions |
|---|---|
| Data integrity, database constraints, migrations, rollback | Can PostgreSQL enforce the invariant? Are uniqueness and partial constraints race-safe, null semantics intentional, indexes justified by actual queries, ordering deterministic, timestamps appropriate, deletion deliberate, existing rows safe and forward/reverse migration behavior explicit? Is money, identity and security data lossless? |
| Architecture, compatibility, second sources of truth | Are writes in services and reads in selectors? Are views/serializers thin? Are business signals, generic utils, premature abstractions, duplicate rules and raw tenant-bypassing model access absent? Do API and HTMX reuse the same domain behavior? |
| Authentication | Who is the caller? Check malformed/revoked credentials, dummy hash work, bearer/session precedence and intended 401 semantics. |
| Authorization, tenant isolation, information disclosure | Can this caller perform this action on this exact object and tenant? Try guessed IDs, client-supplied tenant IDs, authenticated but unauthorized callers, cross-tenant lists and object-existence error differences. Check permissions before work occurs. |
| Input validation, HTTP/API/HTML contracts | Pin methods, routes, status codes, authentication, permissions, content type, field shapes, errors, filtering, deterministic pagination/ordering, idempotency and schema output. Check oversized bodies, invalid encodings, crafted headers and boundary values. Make negative behavior explicit. |
| Transactions, concurrency, idempotency, replay | Identify atomic operations and test two, ten and one hundred concurrent requests where relevant. Look for check-then-write, stale reads, counters, duplicate events/fan-out, worker claims, replay/live races, circuit/rate-limit races and tests that accidentally serialize. |
| Failure recovery, external services | Specify timeout, refusal, malformed/partial response, 429/500, DNS failure, Redis/DB outage, death after commit before acknowledgement, lease-holder death and downstream success before local acknowledgement. State retry, fail-open/closed, dead-letter, degraded-readiness or surfaced-error behavior. |
| SSRF, secret handling, supply chain | Exercise private/localhost/link-local/metadata targets, DNS rebinding and redirect chains where relevant. Check signature replay, stale timestamps, malformed HMAC, credential stuffing, enumeration, unknown-prefix abuse, dependencies and secret exposure. |
| Query correctness and efficiency | Check N+1, repeated tenant lookups, unbounded sets, Python-side filtering/aggregation, full-table loads, indexes, select_related/prefetch_related, pagination stability and unnecessary model hydration. |
| Observability | Useful structured correlation, tenant, key-prefix and status events without raw keys, signing secrets, Authorization headers, sensitive payloads, credential-bearing URIs or enumeration side channels in logs/exceptions/traces. |
| CSP/CSRF, accessibility and UI | Session-authenticated mutations require CSRF. Preserve CSP and API/UI permission parity. Verify semantic elements, keyboard/focus behavior, reduced motion, readable tables and status communicated beyond color. |
| Test validity | Could tests pass against the wrong object, miss the branch, mock away the invariant, bypass middleware/auth, use SQLite for PostgreSQL semantics or duplicate the implementation's algorithm? Call-count assertions alone are not domain proof. |

## 2. API-key design requirements for D01 freeze

These owner requirements must be incorporated into the D01 förspec before it is
locked; this policy does not change the existing D01 DRAFT into a buildable spec.

- Generate prefixes directly from a cryptographic alphabet, not repeated filtering.
- Unknown prefixes must not create unbounded Redis-key cardinality: source-address
  limiting for unknown prefixes, key-specific limiting only for known rows.
- Unknown prefixes perform dummy hash work. Found rows, including revoked keys,
  compare against the stored hash before revocation/environment decisions wherever
  required by the locked design. Define the exact sequence at design freeze.
- Show raw secrets once, store hashes only, enforce scope/environment/revocation,
  and bound last_used_at writes (the build plan requires at most once per minute).
- Bearer credentials take explicit precedence on mixed session/key endpoints;
  malformed Bearer credentials yield the specified 401 rather than session fallback.
- Freeze source-address trust, limits, outage behavior, credential format, hash
  policy, scopes and environment semantics explicitly; never invent them in code.

## 3. Architecture and boundary checks

Authentication and authorization are separate proofs. All exposed surfaces must
respect the exact tenant/object/action boundary. Lock database invariants before
model changes. Validate migration graph, operations/SQL as appropriate, forward
migration, existing-row safety, reverse behavior, names and model/DB parity.

Explicitly map transaction boundaries: Event + Delivery fan-out, outbox writes,
audit entries, replay transitions and security/key operations where the drop needs
them. Flag network calls in DB transactions and overly broad atomic blocks unless
the design justifies them. A dead worker or duplicate request cannot be dismissed
as a happy-path concern.

New dependencies need explicit permission in the locked scope. Existing stdlib,
Django, DRF and PostgreSQL capabilities are preferred. An unauthorized package or
lockfile change is a BLOCKER. Do not change security/CI/Docker infrastructure merely
to make a feature pass.

UI uses server-rendered Django, HTMX for server interaction and Alpine CSP only
for local state. No React SPA, inline script/style or CDN; self-host assets. When
an approved design system exists, implement it using semantic CSS variables, flat
color, editorial Scandinavian hierarchy, restrained radii/surfaces and useful data
density. No gradients, patterned wallpaper, glassmorphism, random cards or decorative
technical text. Do not substitute the builder's taste for the approved design.

## 4. BUILD CONTRACT template

Each task handoff contains:

1. GO / NO-GO, objective and owner authorization reference.
2. Verified branch, HEAD/base, status, current LOCKED förspec and prerequisites.
3. Exact FILES TO TOUCH (enumerate files; a directory is not an exact allowlist).
4. Invariants, risk map, concrete implementation steps and forbidden changes.
5. Tests required: happy path, authorization denial, tenant isolation, invalid and
   nonexistent inputs, duplicate/idempotent requests, concurrency, rollback/failure,
   boundaries, malformed/revoked credentials, outages and bug regressions as relevant.
6. Exact required commands, service requirements and evidence expectations.
7. Explicit stop conditions and any task-specific owner-authorized operations.

Claude receives this contract, never an open-ended "build D01" instruction.
Inspect -> implement -> narrow test -> diagnose -> fix -> rerun -> quality checks
-> full permitted lane. Routine failures belong to the builder until resolved.
Any scope ambiguity or required new path returns to Astra and Mats before changes.

## 5. Fresh adversarial review after every pass

Read Git status and the complete diff before Claude's explanation. Compare
`git diff --name-status`, `git diff --stat`, staged/unstaged diffs and untracked
files against the allowlist. Include newly added files explicitly: an unstaged
untracked file is absent from ordinary git diff. Inspect surrounding code afterward.
Unexplained paths are BLOCKERs, including generated assets, caches, snapshots,
lockfiles, local Claude settings and gate infrastructure.

Try to break the invariants: wrong owner/tenant, nonexistent ID, malformed/revoked
credentials, forged headers, parallel duplicates, replay, stale state, unavailable
Redis, large data, timestamp edges and case normalization where relevant.
Audit every security/data boundary and every changed line for scope discipline.

Scrutinize new noqa/type ignores, warning filters, broad exception catches,
swallowed errors, coverage exclusions, skips, xfails, retry wrappers, fallback
defaults and logging instead of failure. Each needs a locked-contract justification.
Check tests do not pass for the wrong reason. Validate migrations separately.
Do not accept Claude's explanation as proof or invent findings to look thorough.

| Class | Meaning and treatment |
|---|---|
| BLOCKER | Introduced by this work or violates its contract; must resolve before GO. |
| PREREQUISITE | Older issue that genuinely prevents correct completion; must resolve before GO. |
| HYGIENE | Real but unrelated technical debt; backlog only. |
| OBSERVATION | Unproven concern or possible improvement; no task expansion. |

Only BLOCKER/PREREQUISITE go back to Claude. Each remediation packet states exact
file/line, violated invariant, reproduction or reasoning, required outcome and
relevant test. Changes still need to stay within allowed scope. Review the entire
result again after each correction, including secondary defects. After three
correction cycles with a fundamental issue unresolved, report the competing
interpretations to Mats and stop. Final GO requires no unresolved BLOCKER or
PREREQUISITE and green required evidence.

## 6. Quality and evidence

For application work, the normal local lane is:

```text
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy .
bun run typecheck:tools
bun run htmx:check
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run pytest -m "not slow and not e2e"
```

Add task-specific integration/concurrency/security gates and required CI/image
evidence. The BUILD CONTRACT defines the permitted lane. A documentation-only
task may specify a narrower lane with reasons; this never removes CI requirements
or proves the application green. Do not run mutating formatters as read-only checks.

Builder report: CHANGED / EXECUTED HERE / NOT EXECUTED / BEVISAR / BEVISAR INTE /
STAGE (owner). Include actual command tails and distinguish local, historical,
owner and GitHub evidence, tying each to its exact tree/commit. A policy file is
an instruction, not proof of a sandbox, authenticated Claude session or enforced
GitHub protection.

Mats's final gate is short Git status, diff --check, diff --stat, full diff,
Astra's final report and test/check evidence, followed by exact-path staging and
commit. No AI output automatically becomes history. A specific owner instruction
can delegate particular Git operations, but never implicitly grants merge, tag,
production, scope expansion or permission to bypass red checks.
