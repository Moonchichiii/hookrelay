# D00 amendment: permanent T3 operating policy

Version 1.0 · 2026-09-19 · Status: LOCKED for this documentation-only task.

Owner authorization: Mats instructed Astra to make and implement the rules and
push them in the active conversation. Astra may author policy/specification text.
This authorization permits this task's branch creation, exact staging, commit and
push; it does not authorize merging, releases, application implementation, gate
changes or closure of D00.

## Intake

- Base: main at `4bbdcb641c5ee7c8d3969c9bd7635fdcd351c7c3`, verified against GitHub
  main before branching. Starting tree clean.
- Task branch: `d00/t3-agent-policy`, created from that base.
- Current drop: D00, skeleton förspec v1.5.2 LOCKED; D00 remains unclosed.
- Existing governance PR #19 is independent and not incorporated in this branch.
- D01 remains DRAFT, without an exact file allowlist; D01 implementation is NO-GO.
- Only project migration is accounts/0001_initial.py; no migration changes here.
- Docker/PostgreSQL/Redis are not required for policy validation. Existing app,
  integration and security tests remain unchanged.
- Claude CLI authentication reports loggedIn=false. No Claude build is claimed.

## Objective and exact FILES TO TOUCH

Persist the owner-approved architect/builder/adversarial-review workflow without
changing application behavior or declaring unresolved project prerequisites closed.

```text
AGENTS.md
CLAUDE.md
docs/T3-WORKFLOW.md
docs/forspec/D00-t3-policy.md
```

## Contract and risk map

GO for Astra-authored policy documentation only. Claude application build: NO-GO.

- Authority drift: retain owner gates and make delegation task-specific.
- Scope drift: no D01 coding, D11/D12 definition, gate edits or dependency changes.
- Evidence drift: separate written instructions from technical enforcement and
  historical CI evidence; never mark D00 closed or D01 locked through this amendment.
- Workflow omissions: cover intake, all audit dimensions, D01 freeze requirements,
  BUILD CONTRACT, builder loop, fresh review, exact remediation, three-cycle stop,
  quality evidence and owner staging gate.
- Data/tenant/auth/transaction/concurrency/UI/migration risks: no executable change;
  record these as future mandatory audit dimensions rather than claim tested behavior.
- Policy entry points: AGENTS.md and CLAUDE.md point to one shared detailed workflow.

## Validation and stop conditions

Read all four files, compare with the owner's protocol, verify links and scope,
check whitespace and conflict markers, run `git diff --check` and review the full
staged diff including new files before committing. Recheck status and commit file
list, then push only this named branch and verify the remote SHA equals the commit.
Application tests are not required for this text-only contract; required GitHub
checks are not waived and no merge GO is implied by local policy approval.

STOP for out-of-scope paths, unexplained modifications, authority conflicts,
secret exposure, failed validation or push failure. Do not bypass hooks or gates.
Do not configure GitHub security settings, close/merge PR #19 or alter its red gate.
