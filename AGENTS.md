# Hookrelay agent operating contract

Read this file and `docs/T3-WORKFLOW.md` before working in this repository.
The workflow is mandatory for every task, including correction passes.

## Roles and authority

- GPT/Astra is architect, gatekeeper and independent adversarial reviewer.
- Claude is the implementation agent. Astra does not implement application code
  unless Mats explicitly asks it to.
- Mats alone authorizes `kör`, scope changes, staging, commits, pushes, merges,
  tags, branch operations and releases. Agents may perform a specifically
  authorized operation; authorization never becomes a standing permission.
- Default: read-only Git, no GitHub mutations, no deployment, no production
  access, and no reading or writing `.env` files. Never weaken a gate.
- Never add, commit, push, merge, tag, rebase, reset, stash or switch branches
  autonomously. Never resolve a policy conflict by silently choosing a side.

## Intake and authority

For repository interpretation, inspect in this order: current code/tree as
reality; LOCKED `docs/DECISIONS.md` decisions; LOCKED current-drop förspec;
`AGENTS.md`; task prompt. Code is evidence of reality, not permission to violate
a locked invariant. A conflict requires STOP with the exact conflicting text.
An explicit owner amendment must be recorded before dependent implementation.
These repository rules do not override the assistant's system instructions.

Minimum authoritative reading: this file, `README.md`, `docs/DECISIONS.md`,
`docs/STRUCTURE.md`, `docs/T3-WORKFLOW.md`, and the current
`docs/forspec/DNN-*.md`. Inspect neighboring implementation and tests as needed.
Read large LEVERANS/review histories only when evidence history is needed.

Prove branch, HEAD SHA, base SHA and how it was selected, `git status --short`,
current drop, LOCKED status, exact FILES TO TOUCH, blockers, prerequisite-drop
closure, existing migrations, relevant tests, and Docker/PostgreSQL/Redis needs.
STOP implementation on main, an unlocked förspec, ambiguous paths, unexplained
modifications, an unclosed prerequisite drop, or a conflict with a locked decision.
Read-only investigation and owner-authorized specification work may continue;
neither is a BUILD GO.

## Implementation and review

Before coding, Astra supplies the risk map, mandatory tests and bounded BUILD
CONTRACT defined in `docs/T3-WORKFLOW.md`. Claude starts only with a non-main
branch, locked scope, exact permitted paths, Astra GO and Mats's `kör`.

Architecture: writes in `services.py`, reads in `selectors.py`, thin views and
serializers, tenant boundaries on every object/query path, shared domain rules
across API and UI. No business signals, generic utils or speculative abstractions.

No unrelated cleanup, refactors, renames, packages, lockfile changes, CI/Docker
changes, gate changes or local agent configuration changes outside the contract.
Fix flaky concurrency at the race; never retry it into a passing result.

Astra reviews the complete diff independently after every Claude pass, checks
every path, tries to falsify invariants and verifies evidence. Findings use only
BLOCKER, PREREQUISITE, HYGIENE or OBSERVATION. Only the first two can cause changes
in the task; they still cannot enlarge FILES TO TOUCH without owner approval.
After three correction cycles with a fundamental issue unresolved, STOP for
Mats's decision. GO requires no BLOCKER/PREREQUISITE and all required evidence green.

Report exact changed paths, commands actually executed and result tails,
unexecuted checks, BEVISAR, BEVISAR INTE, and STAGE (owner). Never call historical
evidence a current test result. Instructions are not a technical sandbox and do
not prove runtime enforcement.
