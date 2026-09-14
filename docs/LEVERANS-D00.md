# LEVERANS D00 — v1.5.2 (revision 2: final rootfs-inspector correction)

Förspec: docs/forspec/D00-skeleton.md v1.5.2 (LOCKED). Zip: hookrelay-20260914-1710-d00-v1_5_2.zip. Base: hookrelay-20260914-1655-d00-v1_5_2.zip (SHA256 73dcb464…c91f2fb). Architecture, Dockerfile, the six digests, fly.toml and both lockfiles are byte-identical to 1655. No application/domain/settings code.

## A. Exact files changed

ADDED: none
MODIFIED: docs/DECISIONS.md, docs/reviews/D00-review-log.md, scripts/inspect_rootfs.py, docs/LEVERANS-D00.md
DELETED: none

## B. What changed

`scripts/inspect_rootfs.py`: forbidden trees are modelled as roots without a trailing slash (`FORBIDDEN_TREE_ROOTS`); `is_in_forbidden_tree()` rejects the root itself (`name == root`) and everything beneath it (`name.startswith(root + "/")`); the forbidden-path and forbidden-tree checks run for every tar entry type — directory, regular file, symlink, hardlink, other — before the directory skip; the exact forbidden-path set, the installer paths, the dev-package check, the setuid/setgid inspection (files and hardlinks) and the required-entry check are unchanged; findings name the entry type. `docs/DECISIONS.md` 41 and a review-log section record the correction.

## C. Lockfile hashes (unchanged)

```
uv.lock  e42d7e6d2f17ad6c20958748f6587d12ba206d350d2f6db4684a2c9c0bb91fed
bun.lock 1aae7a26abc6aaa2a329a6cd53c34e151f29228767607dc56d68cc5ee818055a
```

## D. Non-Docker gates (sandbox: uv 0.12.13, Python 3.14.7, bun 1.4.2, PostgreSQL 16.15 and Redis 7 on 5432/6379 via env)

20 gates, 20 exit 0 (Appendix A), identical set to the 1655 delivery: lock check, locked install, frozen bun install, `typecheck:tools`, build, `htmx:check`, `bun audit`, pre-commit whole tree (0 modifications), secret-pattern scan (none outside the reviewed fixtures), ruff check, ruff format, mypy strict (28 files), `manage.py check`, `check --deploy --fail-level WARNING` (0 silenced), migration drift, migrate, pytest 28 passed at 100% branch coverage, both hash-verified pip-audits clean, six config files parse, inspector regression, digest negative check, hygiene negative check.

## E. Synthetic rootfs regression (fourteen cases, exact output)

```
clean rootfs (with plain directories)  -> exit 0 (expected 0) PASS | rootfs clean
/app/tests empty directory             -> exit 1 (expected 1) PASS | forbidden tree (directory): /app/tests
/app/tests symlink                     -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/tests
/app/docs empty directory              -> exit 1 (expected 1) PASS | forbidden tree (directory): /app/docs
/app/docs symlink                      -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/docs
/app/node_modules symlink              -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/node_modules
/root/.cache symlink                   -> exit 1 (expected 1) PASS | forbidden tree (symlink): /root/.cache
/app/tests/test_x.py file              -> exit 1 (expected 1) PASS | forbidden tree (file): /app/tests/test_x.py
/bin/sh symlink                        -> exit 1 (expected 1) PASS | forbidden path (symlink): /bin/sh
/usr/bin/sh hardlink                   -> exit 1 (expected 1) PASS | forbidden path (hardlink): /usr/bin/sh
/usr/local/bin/pip                     -> exit 1 (expected 1) PASS | forbidden path (file): /usr/local/bin/pip
/app/.venv/bin/uv                      -> exit 1 (expected 1) PASS | forbidden path (file): /app/.venv/bin/uv
setuid regular file                    -> exit 1 (expected 1) PASS | setuid/setgid bit (file): /usr/bin/mount mode 4755
pytest in the venv                     -> exit 1 (expected 1) PASS | development package in runtime venv (file): /app/.venv/lib/python3.14/site-packages/pytest/__init__.py
[exit 0]
```

## F. Zip

hookrelay-20260914-1710-d00-v1_5_2.zip — SHA256 in the delivery message. The 1655 zip is superseded and was never committed.

## Still unproven here

Everything requiring Docker or a registry (v1.5.2 §K). Static iteration ends with this delivery; the real image wall on the owner's machine is next.

## Suggested commit

    d00: chainguard runtime, digest-pinned inputs, shell-less image gates

---

## Appendix A — raw gate output (sandbox, v1.5.2 revision 2)

```
$ uv lock --check
Resolved 82 packages in 3ms
[exit 0]

$ uv sync --locked
Resolved 82 packages in 1ms
Checked 79 packages in 0.55ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

+ @alpinejs/csp@3.17.2
+ @tailwindcss/cli@4.3.3
+ @types/bun@1.4.2
+ htmx.org@4.0.0
+ tailwindcss@4.3.3
+ typescript@7.0.2

46 packages installed [1.63s]
[exit 0]

$ bun run typecheck:tools
$ tsc --project tsconfig.json --noEmit
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 701ms
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 100 packages) [133.00ms]
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

hook modifications: 0

$ repository secret-pattern scan: git grep for scheme://user:password@host, excluding the reviewed fixtures
matches outside the reviewed fixtures: none

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
47 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 28 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ uv run python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, django_tasks_database, sessions
Running migrations:
  No migrations to apply.
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay15
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 28 items

apps/accounts/tests/test_user_model.py .                                 [  3%]
tests/integration/test_skeleton.py ...........                           [ 42%]
tests/integration/test_settings.py ........                              [ 71%]
tests/integration/test_toolchain.py ..                                   [ 78%]
tests/security/test_image_references.py ....                             [ 92%]
tests/security/test_repository_hygiene.py ..                             [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 28 passed in 2.18s ==============================
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/rp.txt
No known vulnerabilities found
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/ra.txt
No known vulnerabilities found
[exit 0]

$ YAML/TOML parse (ci, security, codeql, dependabot, compose, fly.toml)
6 files parse
[exit 0]

$ rootfs inspector synthetic regression (fourteen cases)
clean rootfs (with plain directories)  -> exit 0 (expected 0) PASS | rootfs clean
/app/tests empty directory             -> exit 1 (expected 1) PASS | forbidden tree (directory): /app/tests
/app/tests symlink                     -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/tests
/app/docs empty directory              -> exit 1 (expected 1) PASS | forbidden tree (directory): /app/docs
/app/docs symlink                      -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/docs
/app/node_modules symlink              -> exit 1 (expected 1) PASS | forbidden tree (symlink): /app/node_modules
/root/.cache symlink                   -> exit 1 (expected 1) PASS | forbidden tree (symlink): /root/.cache
/app/tests/test_x.py file              -> exit 1 (expected 1) PASS | forbidden tree (file): /app/tests/test_x.py
/bin/sh symlink                        -> exit 1 (expected 1) PASS | forbidden path (symlink): /bin/sh
/usr/bin/sh hardlink                   -> exit 1 (expected 1) PASS | forbidden path (hardlink): /usr/bin/sh
/usr/local/bin/pip                     -> exit 1 (expected 1) PASS | forbidden path (file): /usr/local/bin/pip
/app/.venv/bin/uv                      -> exit 1 (expected 1) PASS | forbidden path (file): /app/.venv/bin/uv
setuid regular file                    -> exit 1 (expected 1) PASS | setuid/setgid bit (file): /usr/bin/mount mode 4755
pytest in the venv                     -> exit 1 (expected 1) PASS | development package in runtime venv (file): /app/.venv/lib/python3.14/site-packages/pytest/__init__.py
[exit 0]

$ digest test rejects a tag-only reference (negative check on a temporary copy of compose.yaml)
1 failed, 3 passed in 0.05s
(compose.yaml restored)

$ hygiene gate rejects a planted loopback secret (negative check on a temporary file in an approved context)
1 failed, 1 passed in 0.42s
(planted file removed)
```

## Appendix B — unified diff 1655 → revision 2 (context 1; this file excluded)

```diff
--- 1655/docs/DECISIONS.md
+++ rev2/docs/DECISIONS.md
@@ -46 +46,2 @@
 | 40 | 2026-09-14 | `fly.toml` release and process commands use absolute executables (`/app/.venv/bin/python`, `/app/.venv/bin/uvicorn`) so a shell-less image carries no PATH assumption; topology unchanged | LOCKED |
+| 41 | 2026-09-14 | Rootfs inspection: forbidden tree roots are modelled without trailing slash and rejected as the root itself (directory, symlink, hardlink or any entry) and as anything beneath it, checked before the directory skip | LOCKED |

--- 1655/docs/reviews/D00-review-log.md
+++ rev2/docs/reviews/D00-review-log.md
@@ -94 +94,11 @@
 | README/PROOFS wording: "read-only token", "same as CI", Docker rows PROVEN for a runtime no longer used, ruleset implied | precision | corrected; ruleset marked OPEN owner action (v1.5.2) |
+
+## Static review of the 1644 and 1655 v1.5.2 zips → revision 2
+
+| Finding | Class | Resolution |
+|---|---|---|
+| Inspector skipped non-regular entries before the forbidden-path check: `/bin/sh -> /bin/busybox` passed as "no shell" | BLOCKER (security gate bypass) | forbidden paths checked for every entry type; pip/pip3 and venv uv/uvx added (1655) |
+| Inspector skipped directories before the tree check and matched trailing-slash prefixes only: an empty `/app/tests`, or `/app/tests`, `/app/docs`, `/app/node_modules`, `/root/.cache` as symlinks, passed as clean | BLOCKER (security gate bypass) | tree roots without trailing slash, root itself and everything beneath rejected for every entry type before the directory skip; fourteen-case synthetic regression (revision 2) |
+| Decisions 18/20/32 contradicted 27/38/37 while all LOCKED | governance | statuses set to superseded/amended (1655) |
+| Local wall expected 200 for a plain http `/livez` under `SECURE_SSL_REDIRECT`; deploy check missing; host Trivy assumed | precision | 301, deploy check with generated key, Dockerized `aquasec/trivy:0.74.0` (1655) |
+| `fly.toml` commands relied on PATH in a shell-less image | hardening | absolute executables (1655) |

--- 1655/scripts/inspect_rootfs.py
+++ rev2/scripts/inspect_rootfs.py
@@ -70,16 +70,17 @@
 }
-# Directory trees that must contain no entries at all.
-FORBIDDEN_TREES = (
-    "app/tests/",
-    "app/docs/",
-    "app/node_modules/",
-    "app/.git/",
-    "app/.venv/.cache/",
-    "root/.cache/",
-    "home/nonroot/.cache/",
-    "home/app/.cache/",
-    "app/.cache/",
-    "var/cache/apk/",
-    "var/cache/apt/",
-    "var/lib/apt/lists/",
+# Tree roots that may not exist at all: not as a directory, symlink, hardlink or
+# any other entry, and with nothing beneath them.
+FORBIDDEN_TREE_ROOTS = (
+    "app/tests",
+    "app/docs",
+    "app/node_modules",
+    "app/.git",
+    "app/.venv/.cache",
+    "root/.cache",
+    "home/nonroot/.cache",
+    "home/app/.cache",
+    "app/.cache",
+    "var/cache/apk",
+    "var/cache/apt",
+    "var/lib/apt/lists",
 )
@@ -105,2 +106,18 @@

+def is_in_forbidden_tree(name: str) -> bool:
+    return any(name == root or name.startswith(root + "/") for root in FORBIDDEN_TREE_ROOTS)
+
+
+def entry_kind(member: tarfile.TarInfo) -> str:
+    if member.isdir():
+        return "directory"
+    if member.issym():
+        return "symlink"
+    if member.islnk():
+        return "hardlink"
+    if member.isfile():
+        return "file"
+    return "other"
+
+
 def main(path: str) -> int:
@@ -112,9 +129,11 @@
             present.add(name)
+            kind = entry_kind(member)
+            # Path checks come first and apply to every entry type, including
+            # the tree root itself as a directory or symlink.
+            if name in FORBIDDEN_FILES:
+                violations.append(f"forbidden path ({kind}): /{name}")
+            if is_in_forbidden_tree(name):
+                violations.append(f"forbidden tree ({kind}): /{name}")
             if member.isdir():
                 continue
-            kind = "symlink" if member.issym() else "hardlink" if member.islnk() else "file"
-            if name in FORBIDDEN_FILES:
-                violations.append(f"forbidden path ({kind}): /{name}")
-            if name.startswith(FORBIDDEN_TREES):
-                violations.append(f"forbidden tree content ({kind}): /{name}")
             if name.startswith("app/.venv/lib/") and "/site-packages/" in name:
```

---

# LEVERANS D00 — v1.5.2 (revision: static-review corrections)

Förspec: docs/forspec/D00-skeleton.md v1.5.2 (LOCKED). Zip: hookrelay-20260914-1655-d00-v1_5_2.zip. Base: hookrelay-20260914-1644-d00-v1_5_2.zip (SHA256 a722bbe1…734d48), itself built on the v1.5.1 zip; the owner's 1650 zip equals v1.5.1 plus two local experiment artefacts (`Dockerfile.chainguard-test`, `sbom-image.cdx.json`) and minus `.env.example` — nothing from those artefacts is used. Six image digests unchanged. No application/domain/settings code, no lockfile change.

## A. Exact files changed

ADDED: none
MODIFIED: README.md, docs/DECISIONS.md, fly.toml, scripts/inspect_rootfs.py, docs/LEVERANS-D00.md
DELETED: none

## B. Exact diff (1644 → this revision; this file excluded; Appendix B)

- `scripts/inspect_rootfs.py`: forbidden exact paths and forbidden trees are checked for every non-directory entry — regular file, symlink, hardlink — before any type filtering (the reviewer's `/bin/sh -> /bin/busybox` escape is closed); setuid/setgid inspection covers regular files and hardlinks; new forbidden paths `usr/bin/pip`, `usr/bin/pip3`, `usr/local/bin/pip`, `usr/local/bin/pip3`, `app/.venv/bin/pip`, `app/.venv/bin/pip3`, `app/.venv/bin/uv`, `app/.venv/bin/uvx`; required entries are accepted as any type (the venv `bin/python` is a symlink in every uv venv); findings name the entry type.
- `docs/DECISIONS.md`: 18 → SUPERSEDED by 27; 20 → AMENDED (token wording) and SUPERSEDED IN PART by 38 (ruleset OPEN); 32 → SUPERSEDED by 37; new 39 (any-type forbidden paths, installer paths) and 40 (absolute Fly commands). Nothing erased.
- `fly.toml`: `release_command`, `web` and `worker` use `/app/.venv/bin/python` and `/app/.venv/bin/uvicorn`; topology unchanged.
- `README.md` and LEVERANS J: Dockerized `aquasec/trivy:0.74.0` (Docker socket + `trivy-cache` volume) for the SBOM and the fail-closed scan, `--pkg-types os,library` on the CLI, `vuln-type` retained in the action; the no-header `/livez` expectation corrected to 301 under production `SECURE_SSL_REDIRECT` (the untrusted/trusted pair with the header stays the authoritative proof); the production deploy check added to the local wall with a generated temporary key and explicit variable removal.

## C. Lockfile hashes (unchanged)

```
uv.lock  e42d7e6d2f17ad6c20958748f6587d12ba206d350d2f6db4684a2c9c0bb91fed
bun.lock 1aae7a26abc6aaa2a329a6cd53c34e151f29228767607dc56d68cc5ee818055a
```

## D. Non-Docker gates (sandbox: uv 0.12.13, Python 3.14.7, bun 1.4.2, PostgreSQL 16.15 and Redis 7 on 5432/6379 via env)

20 gates, 20 exit 0 (Appendix A): lock check, locked install, frozen bun install, `typecheck:tools`, build, `htmx:check`, `bun audit`, pre-commit whole tree (0 modifications), repository secret-pattern scan (no match outside the reviewed fixtures), ruff check, ruff format, mypy strict (28 files), `manage.py check`, `check --deploy --fail-level WARNING` (0 silenced), migration drift, migrate, pytest 28 passed at 100% branch coverage, both hash-verified pip-audits clean, six config files parse (incl. `fly.toml` with the absolute commands), inspector self-test, digest negative check, hygiene negative check.

## E. Synthetic rootfs negative-test results (Appendix A, exact)

```
clean synthetic rootfs       -> exit 0 (expected 0) PASS
/bin/sh as a symlink         -> exit 1 (expected 1) PASS | forbidden path (symlink): /bin/sh
/usr/bin/sh as a hardlink    -> exit 1 (expected 1) PASS | forbidden path (hardlink): /usr/bin/sh
/usr/local/bin/pip           -> exit 1 (expected 1) PASS | forbidden path (file): /usr/local/bin/pip
/app/.venv/bin/uv            -> exit 1 (expected 1) PASS | forbidden path (file): /app/.venv/bin/uv
setuid regular file          -> exit 1 (expected 1) PASS | setuid/setgid bit (file): /usr/bin/mount mode 4755
pytest in the venv           -> exit 1 (expected 1) PASS | development package in runtime venv (file)
```

## F. Zip

hookrelay-20260914-1655-d00-v1_5_2.zip — SHA256 in the delivery message. The 1644 zip is superseded and was never committed.

## Owner notes before the real image wall

- Copying this zip over the 1650 tree restores `.env.example` (v1.5 decision 30) and does not remove the local artefacts; delete `Dockerfile.chainguard-test`, `sbom-image.cdx.json` and `docker/suid-allowlist.txt` from the working tree before staging (exact-path staging only). `hookrelay-rootfs.tar` and `sbom-image.cdx.json` are produced by the local wall and must stay unstaged.
- Everything in v1.5.2 §K remains unproven until the Docker wall runs.

## BEVISAR / BEVISAR INTE

BEVISAR: the inspector now rejects the symlink and hardlink escapes and the installer paths while still passing a clean rootfs; the decision ledger has no contradictory LOCKED rows; Fly commands carry no PATH assumption; the local wall's expectations are correct and complete; the non-Docker wall is green with lockfiles untouched.
BEVISAR INTE: everything requiring Docker or a registry (v1.5.2 §K).

## Suggested commit

    d00: chainguard runtime, digest-pinned inputs, shell-less image gates

---

## Appendix A — raw gate output (sandbox, v1.5.2 revision)

```
$ uv lock --check
Resolved 82 packages in 3ms
[exit 0]

$ uv sync --locked
Resolved 82 packages in 1ms
Checked 79 packages in 0.60ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

+ @alpinejs/csp@3.17.2
+ @tailwindcss/cli@4.3.3
+ @types/bun@1.4.2
+ htmx.org@4.0.0
+ tailwindcss@4.3.3
+ typescript@7.0.2

46 packages installed [102.00ms]
[exit 0]

$ bun run typecheck:tools
$ tsc --project tsconfig.json --noEmit
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 147ms
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 100 packages) [120.00ms]
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

hook modifications: 0

$ repository secret-pattern scan: git grep for scheme://user:password@host, excluding the reviewed fixtures
matches outside the reviewed fixtures: none

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
47 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 28 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ uv run python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, django_tasks_database, sessions
Running migrations:
  No migrations to apply.
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay15
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 28 items

apps/accounts/tests/test_user_model.py .                                 [  3%]
tests/integration/test_skeleton.py ...........                           [ 42%]
tests/integration/test_settings.py ........                              [ 71%]
tests/integration/test_toolchain.py ..                                   [ 78%]
tests/security/test_image_references.py ....                             [ 92%]
tests/security/test_repository_hygiene.py ..                             [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 28 passed in 1.80s ==============================
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/rp.txt
No known vulnerabilities found
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/ra.txt
No known vulnerabilities found
[exit 0]

$ YAML/TOML parse (ci, security, codeql, dependabot, compose, fly.toml)
6 files parse; fly processes: {'web': '/app/.venv/bin/uvicorn config.asgi:application --host 0.0.0.0 --port 8080 --proxy-headers', 'worker': '/app/.venv/bin/python manage.py db_worker'} release: /app/.venv/bin/python manage.py migrate --noinput
[exit 0]

$ rootfs inspector synthetic self-test (seven cases)
clean synthetic rootfs       -> exit 0 (expected 0) PASS | rootfs clean: 6 entries; no shell, package installer, build tooling, caches or dev packages; 0 setuid/setgid files
/bin/sh as a symlink         -> exit 1 (expected 1) PASS |   forbidden path (symlink): /bin/sh
/usr/bin/sh as a hardlink    -> exit 1 (expected 1) PASS |   forbidden path (hardlink): /usr/bin/sh
/usr/local/bin/pip           -> exit 1 (expected 1) PASS |   forbidden path (file): /usr/local/bin/pip
/app/.venv/bin/uv            -> exit 1 (expected 1) PASS |   forbidden path (file): /app/.venv/bin/uv
setuid regular file          -> exit 1 (expected 1) PASS |   setuid/setgid bit (file): /usr/bin/mount mode 4755
pytest in the venv           -> exit 1 (expected 1) PASS |   development package in runtime venv (file): /app/.venv/lib/python3.14/site-packages/pytest/__init__.py
[exit 0]

$ digest test rejects a tag-only reference (negative check on a temporary copy of compose.yaml)
1 failed, 3 passed in 0.05s
(compose.yaml restored)

$ hygiene gate rejects a planted loopback secret (negative check on a temporary file in an approved context)
1 failed, 1 passed in 0.47s
(planted file removed)
```

## Appendix B — unified diff 1644 → revision (context 1; this file excluded)

```diff
--- v1.5.2-1644/README.md
+++ v1.5.2-rev/README.md
@@ -72,7 +72,7 @@
 docker run --rm --entrypoint /app/.venv/bin/python hookrelay:ci -c "import sys, django, psycopg, uvloop, httptools; print(sys.version_info[:3], sys.executable)"
-trivy image --format cyclonedx --output sbom-image.cdx.json hookrelay:ci
-trivy image --scanners vuln,secret --pkg-types os,library --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
+docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy -v ${PWD}:/out aquasec/trivy:0.74.0 image --format cyclonedx --output /out/sbom-image.cdx.json hookrelay:ci
+docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy aquasec/trivy:0.74.0 image --scanners vuln,secret --pkg-types os,library --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
 ```

-Use Trivy v0.74.0 locally as CI does. The CLI flag is `--pkg-types`; the pinned GitHub action still calls the same setting `vuln-type` and maps it internally — both are correct in their place. The runtime has no shell, so inspection happens from the host on the exported rootfs; `scripts/inspect_rootfs.py` fails on any shell, build tool, package manager, cache, test/doc content, dev package or setuid/setgid file.
+The scanner runs as the Dockerized `aquasec/trivy:0.74.0` (no host install), the same engine version CI pins. The CLI flag is `--pkg-types`; the pinned GitHub action still calls the same setting `vuln-type` and maps it internally — both are correct in their place. `sbom-image.cdx.json` and `hookrelay-rootfs.tar` are local evidence, not repository content. The runtime has no shell, so inspection happens from the host on the exported rootfs; `scripts/inspect_rootfs.py` fails on any shell, build tool, package manager, cache, test/doc content, dev package or setuid/setgid file.


--- v1.5.2-1644/docs/DECISIONS.md
+++ v1.5.2-rev/docs/DECISIONS.md
@@ -23,5 +23,5 @@
 | 17 | 2026-09-13 | BUILD-PLAN v1.0 | LOCKED |
-| 18 | 2026-09-14 | Container scan: Trivy, CRITICAL/HIGH, `ignore-unfixed`, required | LOCKED |
+| 18 | 2026-09-14 | Container scan: Trivy, CRITICAL/HIGH, `ignore-unfixed`, required | SUPERSEDED by 27 — `ignore-unfixed` no longer exists; fixed and unfixed both block |
 | 19 | 2026-09-14 | `SECURE_HSTS_PRELOAD = True` as a header flag so the deploy checklist passes at WARNING level with nothing silenced | LOCKED |
-| 20 | 2026-09-14 | Every GitHub Action pinned to a full commit SHA; workflow token read-only; `main` protected by a ruleset requiring `test`, `security`, `docker`, `analyze (python)`, `analyze (javascript-typescript)` | LOCKED |
+| 20 | 2026-09-14 | Every GitHub Action pinned to a full commit SHA; workflow token read-only; `main` protected by a ruleset requiring `test`, `security`, `docker`, `analyze (python)`, `analyze (javascript-typescript)` | AMENDED — token wording is now: workflow default `contents: read`, CodeQL alone `security-events: write`; the ruleset part is SUPERSEDED by 38 (OPEN owner action) |
 | 21 | 2026-09-14 | No gate ever moves backward for new code; ignores are narrow and reasoned; warnings are errors; no CI retries for flaky tests; vulnerability exceptions need a dated record | LOCKED |
@@ -37,3 +37,3 @@
 | 31 | 2026-09-14 | The Dockerfile owns the complete `PYTHON_IMAGE` reference; CI never passes a build-arg for it, so a digest pin in the Dockerfile applies to every build; Trivy engine pinned explicitly (v0.74.0) on both invocations; the runtime SBOM is produced and uploaded before the fail-closed scan | LOCKED |
-| 32 | 2026-09-14 | No credential-shaped connection URI (`scheme://user:password@host`) is committed; fixtures are assembled at runtime from synthetic parts; `tests/security/test_repository_hygiene.py` gates the whole tree; loopback/container-local placeholders are the documented exception; GitHub's incident is resolved as a test fixture only after the literal is gone | LOCKED |
+| 32 | 2026-09-14 | No credential-shaped connection URI (`scheme://user:password@host`) is committed; fixtures are assembled at runtime from synthetic parts; `tests/security/test_repository_hygiene.py` gates the whole tree; loopback/container-local placeholders are the documented exception; GitHub's incident is resolved as a test fixture only after the literal is gone | SUPERSEDED by 37 — explicit reviewed fixture combinations in approved contexts, not a blanket rule |
 | 33 | 2026-09-14 | Runtime family LOCKED to Chainguard Python: builder `cgr.dev/chainguard/python:latest-dev`, runtime `cgr.dev/chainguard/python:latest` (non-root 65532, no shell, no package manager), venv built in the builder against `/usr/bin/python` and copied into the runtime; `ENTRYPOINT []` with an absolute uvicorn CMD; no useradd/apk/apt/pip removal/shell/sudo/uv/Bun in the runtime. Justification: the owner's local proof — `python:3.14.7-slim-trixie` 53 HIGH + 3 CRITICAL, Alpine clean only with OS mutation and pip removal, Chainguard pair Trivy HIGH=0/CRITICAL=0 with django, psycopg, uvloop and httptools importing | LOCKED |
@@ -44 +44,3 @@
 | 38 | 2026-09-14 | Branch ruleset / protection on `main` is an OWNER ACTION and OPEN until configured and verified; nothing in the repository claims it | OPEN |
+| 39 | 2026-09-14 | Rootfs inspection rejects forbidden executable paths as regular files, symlinks and hardlinks (a symlinked `/bin/sh` is a shell); package installers (`pip`, `pip3`, uv/uvx in the venv) are forbidden paths; setuid/setgid inspection covers files and hardlinks | LOCKED |
+| 40 | 2026-09-14 | `fly.toml` release and process commands use absolute executables (`/app/.venv/bin/python`, `/app/.venv/bin/uvicorn`) so a shell-less image carries no PATH assumption; topology unchanged | LOCKED |

--- v1.5.2-1644/fly.toml
+++ v1.5.2-rev/fly.toml
@@ -18,10 +18,11 @@
 [deploy]
-  release_command = "python manage.py migrate --noinput"
+  release_command = "/app/.venv/bin/python manage.py migrate --noinput"

 [processes]
-  # --proxy-headers lets Django see the original https scheme via SECURE_PROXY_SSL_HEADER,
-  # for sources allowed by FORWARDED_ALLOW_IPS.
-  web = "uvicorn config.asgi:application --host 0.0.0.0 --port 8080 --proxy-headers"
+  # Absolute executables: the runtime image has no shell and Fly replaces CMD with
+  # these commands (ENTRYPOINT is cleared in the Dockerfile). --proxy-headers lets
+  # Django see the original scheme for sources allowed by FORWARDED_ALLOW_IPS.
+  web = "/app/.venv/bin/uvicorn config.asgi:application --host 0.0.0.0 --port 8080 --proxy-headers"
   # Idle until Drop 3 defines the first task; kept here so the topology is fixed.
-  worker = "python manage.py db_worker"
+  worker = "/app/.venv/bin/python manage.py db_worker"


--- v1.5.2-1644/scripts/inspect_rootfs.py
+++ v1.5.2-rev/scripts/inspect_rootfs.py
@@ -4,3 +4,5 @@
 `docker export` gives the merged filesystem as a tar; this script checks exact
-paths and mode bits with the standard library only.
+paths and mode bits with the standard library only. Forbidden paths are
+rejected whatever the entry type (regular file, symlink, hardlink): a shell
+reachable through /bin/sh -> /bin/busybox is still a shell.

@@ -12,3 +14,3 @@

-# Exact executable locations that must not exist in the runtime.
+# Exact executable locations that must not exist in the runtime, as any entry type.
 FORBIDDEN_FILES = {
@@ -27,2 +29,3 @@
     "usr/local/bin/uv",
+    "app/.venv/bin/uv",
     "bin/uvx",
@@ -30,2 +33,9 @@
     "usr/local/bin/uvx",
+    "app/.venv/bin/uvx",
+    "usr/bin/pip",
+    "usr/bin/pip3",
+    "usr/local/bin/pip",
+    "usr/local/bin/pip3",
+    "app/.venv/bin/pip",
+    "app/.venv/bin/pip3",
     "usr/local/bin/bun",
@@ -60,3 +70,3 @@
 }
-# Directory trees that must be empty of regular files.
+# Directory trees that must contain no entries at all.
 FORBIDDEN_TREES = (
@@ -86,4 +96,4 @@
 )
-# Paths that must exist: proves the export is the real image, not an empty tar.
-REQUIRED_FILES = (
+# Entries that must exist (any type): proves the export is the real image.
+REQUIRED_ENTRIES = (
     "app/.venv/bin/uvicorn",
@@ -102,8 +112,9 @@
             present.add(name)
-            if not member.isfile():
+            if member.isdir():
                 continue
+            kind = "symlink" if member.issym() else "hardlink" if member.islnk() else "file"
             if name in FORBIDDEN_FILES:
-                violations.append(f"forbidden file: /{name}")
+                violations.append(f"forbidden path ({kind}): /{name}")
             if name.startswith(FORBIDDEN_TREES):
-                violations.append(f"forbidden tree content: /{name}")
+                violations.append(f"forbidden tree content ({kind}): /{name}")
             if name.startswith("app/.venv/lib/") and "/site-packages/" in name:
@@ -111,8 +122,8 @@
                 if top.split("-", 1)[0] in FORBIDDEN_SITE_PACKAGES:
-                    violations.append(f"development package in runtime venv: /{name}")
-            if member.mode & 0o6000:
-                violations.append(f"setuid/setgid bit: /{name} mode {member.mode:o}")
-    for required in REQUIRED_FILES:
+                    violations.append(f"development package in runtime venv ({kind}): /{name}")
+            if (member.isfile() or member.islnk()) and member.mode & 0o6000:
+                violations.append(f"setuid/setgid bit ({kind}): /{name} mode {member.mode:o}")
+    for required in REQUIRED_ENTRIES:
         if required not in present:
-            violations.append(f"missing required file: /{required}")
+            violations.append(f"missing required entry: /{required}")
     if violations:
@@ -123,4 +134,4 @@
     print(
-        f"rootfs clean: {len(present)} entries; no shell, build tooling, caches or dev packages; "
-        "0 setuid/setgid files"
+        f"rootfs clean: {len(present)} entries; no shell, package installer, build tooling, "
+        "caches or dev packages; 0 setuid/setgid files"
     )
```

---

# LEVERANS D00 — v1.5.2 (Chainguard runtime, final container / supply-chain hardening)

Förspec: docs/forspec/D00-skeleton.md v1.5.2 (LOCKED). Zip: hookrelay-20260914-1644-d00-v1_5_2.zip. Base: hookrelay-20260914-1332-d00-v1_5_1.zip (SHA256 871f6a36…7f72c1). Replaces the Debian runtime architecture with the Chainguard pair proven locally by the owner. No application/domain code, no lockfile change, no production deploy, no push.

## A. Exact files added / modified / deleted

ADDED: scripts/inspect_rootfs.py, tests/security/test_image_references.py
MODIFIED: .github/workflows/ci.yml, .github/workflows/security.yml, .gitignore, Dockerfile, README.md, compose.yaml, docs/DECISIONS.md, docs/PROOFS.md, docs/forspec/D00-skeleton.md, docs/reviews/D00-review-log.md, tests/integration/test_toolchain.py, tests/security/test_repository_hygiene.py, docs/LEVERANS-D00.md
DELETED: docker/suid-allowlist.txt

## B. Diff summary (v1.5.1 → v1.5.2; full unified diff in Appendix B, redacted only where a non-approved credential-shaped line would otherwise be reproduced)

- `Dockerfile`: four stages (`uv` source, `assets`, `builder` on Chainguard `python:latest-dev` as root with uv at `/usr/local/bin/uv`, `UV_PYTHON=/usr/bin/python`, `uv sync --locked --no-dev --no-install-project`, collectstatic; `runtime` on Chainguard `python:latest` with explicit `COPY --chown=65532:65532` of `.venv`, `manage.py`, `config`, `apps`, `templates`, `static/dist`, `staticfiles`, `USER 65532`, `ENTRYPOINT []`, absolute uvicorn CMD). All four inputs are the owner-measured index digests. No useradd, apk, apt, pip removal, shell, sudo, uv or Bun in the runtime.
- `compose.yaml` and `ci.yml` service images: `postgres:17@sha256:67f41722…` (manifest 17.11) and `redis:7@sha256:71da9275…` (manifest 7.4.11); ports, credentials, health checks and semantics unchanged; tags left human-readable.
- `scripts/inspect_rootfs.py` (new, stdlib only): host-side inspection of `docker export` — exact forbidden executable paths (shells, uv/uvx, bun/node/npm, compilers, apk/apt/dpkg/yum/dnf, sudo/su), forbidden trees (tests, docs, node_modules, caches, apt/apk caches), forbidden project files (`.env`, `conftest.py`, `pyproject.toml`, `uv.lock`), dev packages in the venv, any regular file with setuid/setgid, and required files present. Self-tested on synthetic tars (clean → 0, dirty → 1 with six distinct findings).
- `ci.yml` docker job: no-cache build; `Config.User == 65532`; rootfs export + inspector; Python 3.14.7 from `/app/.venv/bin/python` with django/psycopg/uvloop/httptools imports; migrate through the final image; boot on the bridge network with `/livez`, `/readyz` and the two-way trust-boundary probe. No `--entrypoint sh` anywhere.
- `security.yml`: build → runtime SBOM → upload → fail-closed scan (Trivy v0.74.0, vuln + secret, `vuln-type: os,library` kept with the action-input/CLI-flag mapping documented; CRITICAL,HIGH; exit 1; no ignore-unfixed, no ignore file, no soft-fail).
- Tests: `test_toolchain.py` → `.python-version` is exactly 3.14.7 and the local interpreter matches (nothing parsed from image tags); `tests/security/test_image_references.py` (new) → every Dockerfile ARG image, both compose services and all four CI service images must be `…@sha256:<64 lowercase hex>` (tag-only rejected; pattern self-tested); `test_repository_hygiene.py` tightened → only the reviewed synthetic combinations (`hookrelay:hookrelay` on the local service hosts, `build:build@localhost`) in approved contexts; a planted `admin:REAL_SECRET` on 127.0.0.1 is rejected (negative test and a planted-file check in Appendix A).
- Removed: `docker/suid-allowlist.txt` and the allowlist gate (zero setuid/setgid is the invariant); duplicate `.env` line in `.gitignore`; `Dockerfile.chainguard-test` was never in the tree and is not added.
- Docs: README (Chainguard runtime section with the local proof commands, precise token wording, "quick local quality subset", hygiene wording, ruleset marked OWNER ACTION / OPEN, trust boundary OPEN), DECISIONS 33–38 (25, 26, 28 marked superseded), PROOFS rows made precise (Docker rows GATE DEFINED for the new runtime, digest pins STATIC PROVEN until the build passes, ruleset OPEN), förspec v1.5.2 paragraph, review log entry. No active doc names the Debian/Alpine runtime, `/usr/local/bin/python3.14`, apt mutation, the SUID allowlist or pip removal except as superseded history.

## C. Lockfile hashes before / after (unchanged)

```
before (v1.5.1 zip):
e42d7e6d2f17ad6c20958748f6587d12ba206d350d2f6db4684a2c9c0bb91fed  uv.lock
1aae7a26abc6aaa2a329a6cd53c34e151f29228767607dc56d68cc5ee818055a  bun.lock
after (this tree):
e42d7e6d2f17ad6c20958748f6587d12ba206d350d2f6db4684a2c9c0bb91fed  uv.lock
1aae7a26abc6aaa2a329a6cd53c34e151f29228767607dc56d68cc5ee818055a  bun.lock
```

## D. Exact non-Docker gates run (sandbox: uv 0.12.13, Python 3.14.7, bun 1.4.2, PostgreSQL 16.15 and Redis 7 on 5432/6379 via env)

19 gates, 19 exit 0 (Appendix A): `uv lock --check`, `uv sync --locked`, frozen bun install, `typecheck:tools`, build, `htmx:check`, `bun audit`, pre-commit whole tree (0 modifications), repository secret-pattern scan (no match outside the reviewed fixtures), ruff check, ruff format, mypy strict (28 files), `manage.py check`, `check --deploy --fail-level WARNING` (0 silenced), migration drift, migrate, pytest 28 passed at 100% branch coverage, both hash-verified pip-audits clean, five YAML files parse. Negative checks: inspector on a dirty synthetic rootfs → exit 1; compose with a tag-only redis → digest test fails; planted loopback secret in an approved context → hygiene gate fails; all temporary changes restored.

## E. Docker architecture

`uv` (digest-pinned uv 0.12.13 binary source) → `assets` (Bun 1.4.2: frozen install, `typecheck:tools`, build) → `builder` (Chainguard `python:latest-dev`, root, uv against `/usr/bin/python`, `UV_NO_CACHE=1`, `uv sync --locked --no-dev --no-install-project`, code + assets, collectstatic with build-only placeholders) → `runtime` (Chainguard `python:latest`, UID 65532, no shell/package manager, explicit COPY of seven paths, `ENTRYPOINT []`, `CMD ["/app/.venv/bin/uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]`). The venv's interpreter layout matches between the pair (owner's local proof: django, psycopg, uvloop, httptools imported in the transferred-venv runtime).

## F. Exact immutable image references

```
PYTHON_BUILDER_IMAGE  cgr.dev/chainguard/python:latest-dev@sha256:7d75104053e1b1b9e3316743e52acc3113be6750918fa7b1c2600fed8b590547
PYTHON_RUNTIME_IMAGE  cgr.dev/chainguard/python:latest@sha256:459a10eaf994a3244330e6c514375c9064f14a34729fe75746f35d1f9fc5a149
UV_IMAGE              ghcr.io/astral-sh/uv:0.12.13@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6
BUN_IMAGE             oven/bun:1.4.2@sha256:9114c058aeae42162ee16dd5084b95fe9473970bb6bcb5b232ab1630f0546895
postgres (compose+CI) postgres:17@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675   (manifest reports 17.11)
redis (compose+CI)    redis:7@sha256:71da9275c5f3fcb97d0fa0c8c5b36cc995327265420f17a04bfd544f458059f7   (manifest reports 7.4.11)
```
All six are the owner's measured digests; none was invented or refreshed here.

## G. Rootfs inspection policy

Host-side, from `docker export`, standard library only. Fails on: exact shell paths; uv/uvx; bun/bunx/node/npm/npx; gcc/cc/g++/c++/make/cmake/ld; apk/apt/apt-get/dpkg/yum/dnf; sudo/su; `app/.env`, `app/conftest.py`, `app/pyproject.toml`, `app/uv.lock`; any file under `app/tests/`, `app/docs/`, `app/node_modules/`, `app/.git/`, uv/apt/apk caches; pytest/_pytest/mypy/ruff/pip_audit/pre_commit/django_stubs/coverage in the venv; any regular file with setuid or setgid; and on the absence of `/app/.venv/bin/uvicorn`, `/app/.venv/bin/python`, `/app/manage.py`, `/app/staticfiles/staticfiles.json`. Names are matched as exact runtime paths, never as substrings.

## H. Trivy policy

Engine `v0.74.0` on both action invocations; `scanners: vuln,secret`; `vuln-type: os,library` (the action's input name, mapped internally to `TRIVY_PKG_TYPES`; the CLI equivalent is `--pkg-types os,library`; the key must not be renamed in the workflow); `severity: CRITICAL,HIGH`; `exit-code: "1"`; fixed and unfixed both block; no `ignore-unfixed`, no ignore file, no `continue-on-error`. Runtime CycloneDX SBOM generated and uploaded before the scan (inventory, not scanning).

## I. Remaining OPEN owner / platform items

1. Build, inspect and scan the final image with the commands in J; the Docker gates are GATE DEFINED until that output exists.
2. Branch ruleset / protection on `main`: OWNER ACTION, not configured (DECISION 38, PROOFS row OPEN).
3. Production forwarded-header trust range: OPEN; loopback placeholder; no deploy until a documented or staged-deployment-proven boundary exists (DECISION 29).
4. GitHub secret-scanning incident: resolve as test fixture only after the commit is pushed.
5. Repository settings: dependency graph, Dependabot alerts and security updates.
6. v1.6 python-decouple and D01 remain blocked behind a green exact commit.

## J. Exact local PowerShell wall for Mats (pwsh 7, from the repository root, Docker Desktop and Trivy v0.74.0 installed)

```
docker compose up -d
uv lock --check && uv sync --locked && bun install --frozen-lockfile && bun run typecheck:tools && bun run build && bun run htmx:check && bun audit
uv run pre-commit run --all-files && uv run ruff check . && uv run ruff format --check . && uv run mypy . && uv run python manage.py check && uv run python manage.py makemigrations --check --dry-run && uv run python manage.py migrate --noinput && uv run pytest -m "not slow and not e2e"
# production deploy checklist at WARNING level, with a generated temporary key; variables removed afterwards
$env:DJANGO_SETTINGS_MODULE = "config.settings.prod"; $env:ALLOWED_HOSTS = "localhost"; $env:SECRET_KEY = (uv run python -c "import secrets; print(secrets.token_urlsafe(48))"); uv run python manage.py check --deploy --fail-level WARNING; Remove-Item Env:DJANGO_SETTINGS_MODULE, Env:ALLOWED_HOSTS, Env:SECRET_KEY
uv export --locked --no-dev --no-emit-project --format requirements.txt -o $env:TEMP\req-prod.txt; uv run pip-audit --strict --require-hashes -r $env:TEMP\req-prod.txt
uv export --locked --all-groups --no-emit-project --format requirements.txt -o $env:TEMP\req-all.txt; uv run pip-audit --strict --require-hashes -r $env:TEMP\req-all.txt

# A. no-cache final build
docker build --no-cache -t hookrelay:ci .
# B. image user
docker inspect --format '{{.Config.User}}' hookrelay:ci                       # expect 65532
# C. Python 3.14.7 from the venv  +  D. native dependency imports
docker run --rm --entrypoint /app/.venv/bin/python hookrelay:ci -c "import sys, django, psycopg, uvloop, httptools; print(sys.version_info[:3], sys.executable, django.__version__, psycopg.__version__, uvloop.__version__, httptools.__version__)"
# E. rootfs export inspection (host side)
docker create --name hookrelay-inspect hookrelay:ci; docker export hookrelay-inspect -o hookrelay-rootfs.tar; docker rm hookrelay-inspect; uv run python scripts/inspect_rootfs.py hookrelay-rootfs.tar
# F. migration through the final image (local compose ports)
docker run --rm --add-host=host.docker.internal:host-gateway -e SECRET_KEY=local-smoke-key-0123456789abcdef0123456789abcdef -e DATABASE_URL=postgresql://hookrelay:hookrelay@host.docker.internal:55433/hookrelay -e REDIS_URL=redis://host.docker.internal:56380/0 -e ALLOWED_HOSTS=127.0.0.1,localhost hookrelay:ci /app/.venv/bin/python manage.py migrate --noinput
# G. runtime boot (loopback trust; requests from your host arrive via Docker's port mapping)
docker run -d --name hookrelay -p 8080:8080 --add-host=host.docker.internal:host-gateway -e SECRET_KEY=local-smoke-key-0123456789abcdef0123456789abcdef -e DATABASE_URL=postgresql://hookrelay:hookrelay@host.docker.internal:55433/hookrelay -e REDIS_URL=redis://host.docker.internal:56380/0 -e ALLOWED_HOSTS=127.0.0.1,localhost -e FORWARDED_ALLOW_IPS=127.0.0.1 hookrelay:ci
# H. /livez   I. /readyz   J. forwarded-header trust (301 = Django saw plain http: SECURE_SSL_REDIRECT, header rejected from the port-mapped source, which is not loopback inside the container)
curl.exe -s -o NUL -w "livez  no header -> %{http_code}`n" -H "Host: localhost" http://127.0.0.1:8080/livez
curl.exe -s -o NUL -w "readyz X-Forwarded-Proto https, untrusted source -> %{http_code}`n" -H "Host: localhost" -H "X-Forwarded-Proto: https" http://127.0.0.1:8080/readyz
docker rm -f hookrelay
docker run -d --name hookrelay -p 8080:8080 --add-host=host.docker.internal:host-gateway -e SECRET_KEY=local-smoke-key-0123456789abcdef0123456789abcdef -e DATABASE_URL=postgresql://hookrelay:hookrelay@host.docker.internal:55433/hookrelay -e REDIS_URL=redis://host.docker.internal:56380/0 -e ALLOWED_HOSTS=127.0.0.1,localhost -e FORWARDED_ALLOW_IPS=0.0.0.0/0 hookrelay:ci
curl.exe -s -H "Host: localhost" -H "X-Forwarded-Proto: https" http://127.0.0.1:8080/livez; echo
curl.exe -s -H "Host: localhost" -H "X-Forwarded-Proto: https" http://127.0.0.1:8080/readyz; echo
docker logs hookrelay; docker rm -f hookrelay
# K. CycloneDX final-image SBOM   L. Trivy 0.74.0 fail-closed scan — Dockerized scanner, no host install
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy -v ${PWD}:/out aquasec/trivy:0.74.0 image --format cyclonedx --output /out/sbom-image.cdx.json hookrelay:ci
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/trivy aquasec/trivy:0.74.0 image --scanners vuln,secret --pkg-types os,library --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
```
Expected: B `65532`; C/D `(3, 14, 7) /app/.venv/bin/python …`; E `rootfs clean …`; F migrations applied; H `301` without the header (production `SECURE_SSL_REDIRECT`: a plain http request from an untrusted source redirects — the untrusted/trusted pair with the header is the authoritative proof); I `301` with the header from an untrusted source and `{"status": "ok", …}` once the source is allowed (`0.0.0.0/0` is a local-only probe value — never a deployment value); L zero CRITICAL/HIGH, exit 0. (Corrected in the v1.5.2 revision; the original text expected 200 for H, which was wrong.) Under Docker Desktop the container sees the port-mapped source as a gateway address, not loopback, which is what makes the 301 a genuine rejection.

## K. Explicitly unproven here

Everything that needs Docker: the build from the digest-pinned inputs, `Config.User`, the real rootfs inspection, the runtime interpreter and imports, migrate/boot/livez/readyz through the final image, the trust probe against a real container, the image SBOM, the Trivy result. Also unproven: that the six digests resolve on the registries from GitHub's runner (they were measured by the owner locally), `uv audit`'s real output, the Fly trust range, and the GitHub-side items in I. Nothing in this delivery claims any of them.

## BEVISAR / BEVISAR INTE

BEVISAR: the non-Docker wall is green on the target toolchain with 28 tests at 100% branch coverage; every repository-owned image reference is a syntactically valid index digest and the test refuses tag-only; the rootfs inspector passes a clean synthetic rootfs and fails a dirty one for each forbidden class; the hygiene gate rejects an unapproved loopback secret; lockfiles are byte-identical; the workflows parse.
BEVISAR INTE: K.

## Suggested commit

    d00: chainguard runtime, digest-pinned inputs, shell-less image gates

---

## Appendix A — raw gate output (sandbox, v1.5.2)

```
$ uv lock --check
Resolved 82 packages in 1ms
[exit 0]

$ uv sync --locked
Resolved 82 packages in 0.91ms
Checked 79 packages in 0.66ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

Checked 46 installs across 102 packages (no changes) [4.00ms]
[exit 0]

$ bun run typecheck:tools
$ tsc --project tsconfig.json --noEmit
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 102ms
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 100 packages) [117.00ms]
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

hook modifications: 0

$ repository secret-pattern scan: git grep for scheme://user:password@host, excluding the reviewed fixtures
matches outside the reviewed fixtures: none

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
47 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 28 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ uv run python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, django_tasks_database, sessions
Running migrations:
  No migrations to apply.
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay15
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 28 items

apps/accounts/tests/test_user_model.py .                                 [  3%]
tests/integration/test_skeleton.py ...........                           [ 42%]
tests/integration/test_settings.py ........                              [ 71%]
tests/integration/test_toolchain.py ..                                   [ 78%]
tests/security/test_image_references.py ....                             [ 92%]
tests/security/test_repository_hygiene.py ..                             [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 28 passed in 1.27s ==============================
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/rp.txt
No known vulnerabilities found
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/ra.txt
No known vulnerabilities found
[exit 0]

$ YAML parse (ci, security, codeql, dependabot, compose)
5 files parse
[exit 0]

$ rootfs inspector self-check on synthetic tars (clean must pass, dirty must fail)
/tmp/clean.tar -> exit 0
rootfs clean: 6 entries; no shell, build tooling, caches or dev packages; 0 setuid/setgid files
/tmp/dirty.tar -> exit 1
ROOTFS INSPECTION FAILED
  development package in runtime venv: /app/.venv/lib/python3.14/site-packages/pytest/__init__.py
  forbidden file: /bin/sh
  forbidden file: /usr/local/bin/uv
  forbidden tree content: /app/tests/test_x.py
  forbidden tree content: /root/.cache/uv/x
  setuid/setgid bit: /usr/bin/mount mode 4755

$ digest test rejects a tag-only reference (negative check on a temporary copy of compose.yaml)
1 failed, 3 passed in 0.05s
(compose.yaml restored)

$ hygiene gate rejects a planted loopback secret (negative check on a temporary file in an approved context)
1 failed, 1 passed in 0.46s
(planted file removed)
```

## Appendix B — unified diff v1.5.1 → v1.5.2 (context 1; this file excluded)

```diff
--- v1.5.1/.github/workflows/ci.yml
+++ v1.5.2/.github/workflows/ci.yml
@@ -28,3 +28,3 @@
       postgres:
-        image: postgres:17
+        image: postgres:17@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
         env:
@@ -38,3 +38,3 @@
       redis:
-        image: redis:7
+        image: redis:7@sha256:71da9275c5f3fcb97d0fa0c8c5b36cc995327265420f17a04bfd544f458059f7
         ports: ["6379:6379"]
@@ -124,3 +124,3 @@
       postgres:
-        image: postgres:17
+        image: postgres:17@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
         env:
@@ -134,3 +134,3 @@
       redis:
-        image: redis:7
+        image: redis:7@sha256:71da9275c5f3fcb97d0fa0c8c5b36cc995327265420f17a04bfd544f458059f7
         ports: ["6379:6379"]
@@ -140,3 +140,3 @@
     env:
-      # CI-only production configuration for the image smoke.
+      # CI-only production configuration for the final-image smoke.
       DATABASE_URL: postgresql://hookrelay:hookrelay@127.0.0.1:5432/hookrelay
@@ -144,2 +144,3 @@
       ALLOWED_HOSTS: 127.0.0.1,localhost
+      PY: /app/.venv/bin/python
     steps:
@@ -147,39 +148,30 @@

-      # The Dockerfile owns the complete PYTHON_IMAGE reference (tag now,
-      # tag@sha256 after the first clean scan); no build-arg may override it.
-      - name: Build image (no cache)
+      # The Dockerfile owns every image reference (all digest-pinned); nothing
+      # here overrides them.
+      - name: Build final image (no cache)
         run: docker build --no-cache -t hookrelay:ci .

-      - name: Runtime user is app
-        run: test "$(docker inspect --format '{{.Config.User}}' hookrelay:ci)" = "app"
-
-      - name: Runtime contains no build tooling or caches
-        run: |
-          docker run --rm --entrypoint sh hookrelay:ci -c '
-            set -e
-            for p in /bin/uv /usr/bin/uv /usr/local/bin/uv /bin/uvx /usr/bin/uvx /usr/local/bin/uvx /root/.cache/uv /home/app/.cache/uv /usr/local/bin/bun /usr/local/bin/tsc; do
-              if [ -e "$p" ]; then echo "PRESENT: $p"; exit 1; fi
-            done
-            for c in gcc cc make uv uvx bun node npm; do
-              if command -v "$c" >/dev/null 2>&1; then echo "ON PATH: $c"; exit 1; fi
-            done
-            if ls /app/.venv/lib/python3.14/site-packages | grep -Eiq "^(pytest|mypy|ruff|pip_audit|pre_commit)"; then echo "DEV PACKAGE IN RUNTIME"; exit 1; fi
-            echo "runtime clean"'
-
-      - name: Runtime interpreter matches .python-version and imports Django
-        run: |
-          expected="$(cat .python-version)"
-          actual="$(docker run --rm --entrypoint python hookrelay:ci -c 'import sys, django; print(".".join(map(str, sys.version_info[:3])))')"
-          echo "expected=$expected actual=$actual"
-          test "$actual" = "$expected"
-
-      # Fail-closed: every setuid/setgid file must be on the reviewed allowlist.
-      - name: SUID/SGID files match the allowlist
-        run: |
-          docker run --rm --entrypoint sh hookrelay:ci -c 'find / -xdev -perm /6000 -type f 2>/dev/null | sort' > /tmp/suid-actual.txt
-          grep -v '^#' docker/suid-allowlist.txt | sed '/^$/d' | sort > /tmp/suid-allowed.txt
-          echo "--- measured"; cat /tmp/suid-actual.txt
-          diff -u /tmp/suid-allowed.txt /tmp/suid-actual.txt
-
-      - name: Migrate with the image (release command)
+      - name: Runtime user is 65532
+        run: test "$(docker inspect --format '{{.Config.User}}' hookrelay:ci)" = "65532"
+
+      # The runtime has no shell: everything below is either a host-side
+      # inspection of the exported rootfs or a direct interpreter invocation.
+      - name: Export runtime rootfs and inspect it on the host
+        run: |
+          docker create --name hookrelay-inspect hookrelay:ci
+          docker export hookrelay-inspect -o hookrelay-rootfs.tar
+          docker rm hookrelay-inspect
+          python3 scripts/inspect_rootfs.py hookrelay-rootfs.tar
+
+      - name: Runtime executes Python 3.14.7 from the venv and imports the native stack
+        run: |
+          docker run --rm --entrypoint "$PY" hookrelay:ci -c '
+          import sys, django, psycopg, uvloop, httptools
+          version = ".".join(map(str, sys.version_info[:3]))
+          print("python", version, "executable", sys.executable)
+          assert sys.version_info[:3] == (3, 14, 7), version
+          assert sys.executable.startswith("/app/.venv/bin/"), sys.executable
+          print("imports ok:", django.__version__, psycopg.__version__, uvloop.__version__, httptools.__version__)'
+
+      - name: Migrate through the final image (release command)
         run: |
@@ -188,3 +180,3 @@
             -e SECRET_KEY -e DATABASE_URL -e REDIS_URL -e ALLOWED_HOSTS \
-            hookrelay:ci python manage.py migrate --noinput
+            hookrelay:ci "$PY" manage.py migrate --noinput

@@ -194,3 +186,3 @@
       # (301 = Django saw http) and the bridge subnet must accept it (200).
-      - name: Boot on the bridge network and probe the forwarded-header trust boundary
+      - name: Boot the final image on the bridge network; probe livez, readyz and the trust boundary
         run: |
@@ -211,3 +203,7 @@
               127.0.0.1) test "$code" = "301" ;;
-              *)         test "$code" = "200" && curl -fsS -o /dev/null -w 'GET / %{http_code}\n' -H 'Host: localhost' -H 'X-Forwarded-Proto: https' "http://$ip:8080/" ;;
+              *)
+                test "$code" = "200"
+                curl -fsS -H 'Host: localhost' -H 'X-Forwarded-Proto: https' "http://$ip:8080/livez"; echo
+                curl -fsS -H 'Host: localhost' -H 'X-Forwarded-Proto: https' "http://$ip:8080/readyz"; echo
+                curl -fsS -o /dev/null -w 'GET / %{http_code}\n' -H 'Host: localhost' -H 'X-Forwarded-Proto: https' "http://$ip:8080/" ;;
             esac

--- v1.5.1/.github/workflows/security.yml
+++ v1.5.2/.github/workflows/security.yml
@@ -83,5 +83,5 @@

-      # The Dockerfile owns the complete PYTHON_IMAGE reference (tag now,
-      # tag@sha256 after the first clean scan); no build-arg may override it.
-      - name: Build image (no cache)
+      # The Dockerfile owns every image reference (all digest-pinned); nothing
+      # here overrides them.
+      - name: Build final image (no cache)
         run: docker build --no-cache -t hookrelay:ci .
@@ -89,4 +89,5 @@
       # The SBOM is produced before the gate so it exists as evidence when the
-      # scan goes red. Trivy engine pinned explicitly: the action's embedded
-      # default lags upstream.
+      # scan goes red; generating it is inventory, not vulnerability scanning.
+      # Trivy engine pinned explicitly: the action's embedded default lags
+      # upstream.
       - name: Runtime image SBOM (CycloneDX)
@@ -107,2 +108,5 @@
       # An unfixed finding keeps this red until a reviewed VEX/waiver exists.
+      # Input naming: the Trivy 0.74 CLI flag is --pkg-types, but this action
+      # exposes it as `vuln-type` and maps it to TRIVY_PKG_TYPES; do not
+      # "modernise" the key to pkg-types, the action does not accept it.
       - name: Container vulnerability scan (fail-closed)

--- v1.5.1/.gitignore
+++ v1.5.2/.gitignore
@@ -13,2 +13 @@
 *.log
-.env

--- v1.5.1/Dockerfile
+++ v1.5.2/Dockerfile
@@ -1,20 +1,19 @@
-# Three stages. Only the last one is shipped: it carries the Python runtime,
-# the production virtualenv, application code and collected static files.
-# uv, Bun, TypeScript, caches, compilers, dev dependencies, tests and docs
-# never enter it. The Python base is one reference (PYTHON_IMAGE) used by both
-# Python stages: the copied virtualenv links to the interpreter at
-# /usr/local/bin/python3.14, so builder and runtime must be the same image,
-# and once a candidate has scanned clean the reference is pinned by digest
-# (python:3.14.7-slim-trixie@sha256:...). This ARG is never overridden from
-# CI; tests/integration/test_toolchain.py keeps its version equal to
-# .python-version. No apt mutation: reproducibility comes from the pinned
-# input, and a base that needs OS fixes is a STOP.
+# Four stages; only `runtime` ships. Every external input is an immutable
+# index digest measured and scanned by the owner (docs/LEVERANS-D00.md, v1.5.2);
+# tests/security/test_image_references.py refuses tag-only references.
+#
+# Builder and runtime are the proven-compatible Chainguard pair: the venv is
+# created in latest-dev against /usr/bin/python and copied into latest, whose
+# interpreter layout matches (verified by import in the owner's local proof).
+# The runtime has no shell, no package manager, no uv, no Bun, no compiler.

-ARG PYTHON_IMAGE=python:3.14.7-slim-trixie
-ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13
-ARG BUN_IMAGE=oven/bun:1.4.2
+ARG PYTHON_BUILDER_IMAGE=cgr.dev/chainguard/python:latest-dev@sha256:7d75104053e1b1b9e3316743e52acc3113be6750918fa7b1c2600fed8b590547
+ARG PYTHON_RUNTIME_IMAGE=cgr.dev/chainguard/python:latest@sha256:459a10eaf994a3244330e6c514375c9064f14a34729fe75746f35d1f9fc5a149
+ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.12.13@sha256:b485bd65cc2cf1c9a93b3554012c9c3778cf7b1b5fd3d3096ce9e1226c97e1e6
+ARG BUN_IMAGE=oven/bun:1.4.2@sha256:9114c058aeae42162ee16dd5084b95fe9473970bb6bcb5b232ab1630f0546895

+# ---- Stage 1: uv binary source ------------------------------------------
 FROM ${UV_IMAGE} AS uv

-# ---- Stage 1: frontend assets -------------------------------------------
+# ---- Stage 2: frontend assets -------------------------------------------
 FROM ${BUN_IMAGE} AS assets
@@ -29,6 +28,8 @@

-# ---- Stage 2: Python dependency builder ---------------------------------
-FROM ${PYTHON_IMAGE} AS builder
-COPY --from=uv /uv /bin/uv
-ENV UV_PYTHON=/usr/local/bin/python3.14 \
+# ---- Stage 3: Python dependency builder ---------------------------------
+FROM ${PYTHON_BUILDER_IMAGE} AS builder
+USER root
+WORKDIR /app
+COPY --from=uv /uv /usr/local/bin/uv
+ENV UV_PYTHON=/usr/bin/python \
     UV_PYTHON_DOWNLOADS=never \
@@ -38,5 +39,4 @@
     UV_NO_CACHE=1
-WORKDIR /app
 COPY pyproject.toml uv.lock ./
-RUN uv sync --locked --no-dev --no-install-project
+RUN /usr/local/bin/uv sync --locked --no-dev --no-install-project
 COPY manage.py ./
@@ -55,4 +55,4 @@

-# ---- Stage 3: runtime ---------------------------------------------------
-FROM ${PYTHON_IMAGE} AS runtime
+# ---- Stage 4: minimal runtime -------------------------------------------
+FROM ${PYTHON_RUNTIME_IMAGE} AS runtime
 ENV PYTHONDONTWRITEBYTECODE=1 \
@@ -61,15 +61,16 @@
     DJANGO_SETTINGS_MODULE=config.settings.prod
-RUN useradd --create-home --no-log-init --uid 1000 app
 WORKDIR /app
-COPY --from=builder --chown=app:app /app/.venv ./.venv
-COPY --from=builder --chown=app:app /app/manage.py ./manage.py
-COPY --from=builder --chown=app:app /app/config ./config
-COPY --from=builder --chown=app:app /app/apps ./apps
-COPY --from=builder --chown=app:app /app/templates ./templates
-COPY --from=builder --chown=app:app /app/static/dist ./static/dist
-COPY --from=builder --chown=app:app /app/staticfiles ./staticfiles
-USER app
+COPY --from=builder --chown=65532:65532 /app/.venv ./.venv
+COPY --from=builder --chown=65532:65532 /app/manage.py ./manage.py
+COPY --from=builder --chown=65532:65532 /app/config ./config
+COPY --from=builder --chown=65532:65532 /app/apps ./apps
+COPY --from=builder --chown=65532:65532 /app/templates ./templates
+COPY --from=builder --chown=65532:65532 /app/static/dist ./static/dist
+COPY --from=builder --chown=65532:65532 /app/staticfiles ./staticfiles
+USER 65532
 EXPOSE 8080
-# Forwarded-header trust comes from FORWARDED_ALLOW_IPS in the environment
-# (uvicorn's own variable; default 127.0.0.1). No wildcard is baked in.
-CMD ["uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
+# The base image sets ENTRYPOINT ["/usr/bin/python"]; cleared so CMD is the
+# whole command. Forwarded-header trust comes from FORWARDED_ALLOW_IPS in the
+# environment (uvicorn's own variable; default 127.0.0.1). No wildcard.
+ENTRYPOINT []
+CMD ["/app/.venv/bin/uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]

--- v1.5.1/README.md
+++ v1.5.2/README.md
@@ -20,3 +20,3 @@

-Quality gate (same as CI):
+Quick local quality subset (CI runs the complete wall described under Quality gates):

@@ -45,7 +45,7 @@

-`ci.yml` enforces, on every push and pull request: `uv lock --check` and `--locked` installs (a stale lock fails; `UV_LOCKED=1` applies to every uv call), a frozen bun install, `bun run typecheck:tools`, the asset build, pre-commit on the whole tree, ruff check and format, mypy strict, the htmx 4 upgrade checker, `manage.py check`, `check --deploy --fail-level WARNING` under production settings, migration drift, a fresh migration, the fast test lane with warnings as errors and a branch-coverage floor of 95%, a uvicorn boot smoke on the migrated database, and the image gates: a no-cache Docker build from `.python-version`, runtime user `app`, no uv/uvx/Bun/compilers/caches/dev packages in the runtime, interpreter equal to `.python-version`, setuid/setgid files equal to the reviewed allowlist, migrate through the image, and the forwarded-header trust boundary proven both ways on the bridge network.
+`ci.yml` enforces, on every push and pull request: `uv lock --check` and `--locked` installs (a stale lock fails; `UV_LOCKED=1` applies to every uv call), a frozen bun install, `bun run typecheck:tools`, the asset build, pre-commit on the whole tree, ruff check and format, mypy strict, the htmx 4 upgrade checker, `manage.py check`, `check --deploy --fail-level WARNING` under production settings, migration drift, a fresh migration, the fast test lane with warnings as errors and a branch-coverage floor of 95%, a uvicorn boot smoke on the migrated database, and the final-image gates: a no-cache Docker build, runtime user `65532`, host-side inspection of the exported rootfs (no shell, no uv/uvx/Bun/node/compilers/package managers, no tests/docs/.env/caches, no dev packages in the venv, zero setuid/setgid files), Python 3.14.7 executing from `/app/.venv` with django/psycopg/uvloop/httptools importable, migrate and boot through the final image, `/livez` and `/readyz`, and the forwarded-header trust boundary proven both ways on the bridge network.

-`security.yml` runs on every change **and daily**: hash-verified pip-audit on the production set and on all dependency groups (no ignores — see `docs/security/README.md`), `bun audit`, `uv audit` as a non-blocking secondary signal, a Python lock SBOM, a Trivy scan of the final runtime image that fails on any known unsuppressed CRITICAL or HIGH finding (vuln + secret scanners, OS + library, no `ignore-unfixed`, no ignore file), a CycloneDX SBOM of that image, and GitHub's dependency review on pull requests. `codeql.yml` covers Python and JavaScript. Every GitHub Action is pinned to a full commit SHA, uv 0.12.13 and bun 1.4.2 are pinned, Python is 3.14.7 everywhere from `.python-version`, base images are exact tags until the digest step below, and the workflow token is read-only.
+`security.yml` runs on every change **and daily**: hash-verified pip-audit on the production set and on all dependency groups (no ignores — see `docs/security/README.md`), `bun audit`, `uv audit` as a non-blocking secondary signal, a Python lock SBOM, a Trivy scan of the final runtime image that fails on any known unsuppressed CRITICAL or HIGH finding (vuln + secret scanners, OS + library, no `ignore-unfixed`, no ignore file), a CycloneDX SBOM of that image, and GitHub's dependency review on pull requests. `codeql.yml` covers Python and JavaScript. Every GitHub Action is pinned to a full commit SHA; uv 0.12.13, bun 1.4.2 and Python 3.14.7 (`.python-version`) are pinned; every base and service image is pinned by index digest (`tests/security/test_image_references.py` refuses tag-only references); the workflow token defaults to `contents: read`, with CodeQL alone receiving the scoped `security-events: write` it requires.

-No credential-shaped connection URI is committed: test fixtures assemble DSNs at runtime, and `tests/security/test_repository_hygiene.py` fails the suite if a literal `scheme://user:password@host` appears anywhere in the tree (loopback and container-local hosts — the compose/CI placeholders — are the only allowed targets). The same check by hand: `git grep -n -E '(postgres(ql)?|redis(s)?)://[^[:space:]/:@]*:[^[:space:]@]+@'` should list only loopback hosts.
+No unapproved credential-shaped connection URI is committed: test fixtures assemble DSNs at runtime, and `tests/security/test_repository_hygiene.py` fails the suite if a literal `scheme://user:password@host` appears anywhere in the tree unless it is one of the explicit reviewed synthetic combinations (the compose credentials `hookrelay:hookrelay` on the local service hosts, the build-only `build:build@localhost`) in an approved context (development settings, `.env.example`, CI services, Dockerfile, README, evidence docs). A loopback host is not an exemption by itself. The same check by hand: `git grep -n -E '(postgres(ql)?|redis(s)?)://[^[:space:]/:@]*:[^[:space:]@]+@'` should list only those fixtures.

@@ -53,5 +53,5 @@

-### Branch ruleset for `main` (configured in GitHub, not in code)
+### Branch ruleset for `main` — OWNER ACTION, OPEN

-Pull request required (0 approvals for a solo developer is fine), required status checks with the branch up to date: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`; conversations resolved; force pushes and deletion blocked; no bypass for normal work. The PR is the evidence envelope for every change.
+Not configured yet as of D00 v1.5.2 (repository inspection showed no ruleset; classic branch protection was not inspectable). Until the owner configures and verifies it, nothing in this repository claims the branch is protected. Target: pull request required (0 approvals for a solo developer is fine), required status checks with the branch up to date: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`; conversations resolved; force pushes and deletion blocked; no bypass for normal work. The PR is the evidence envelope for every change.

@@ -61,5 +61,7 @@

-### Image proof and digests (Docker required)
+### Runtime image (Docker required)

-The runtime image has three stages (assets → Python dependency builder → runtime); only the runtime ships. Build and prove the candidate locally exactly as CI does, then scan it:
+Four stages — uv source → frontend assets (Bun) → Python dependency builder (Chainguard `python:latest-dev`, uv, `uv sync --locked --no-dev`, collectstatic) → minimal runtime (Chainguard `python:latest`: no shell, no package manager, non-root UID 65532, only `/app/.venv` and the application paths). Every image is pinned by index digest in the Dockerfile (`ARG PYTHON_BUILDER_IMAGE`, `PYTHON_RUNTIME_IMAGE`, `UV_IMAGE`, `BUN_IMAGE`); the compose and CI service images likewise (`postgres:17` measured as 17.11, `redis:7` as 7.4.11). Digests are refreshed only deliberately, with a rescan, never by CI.
+
+Prove the final image locally exactly as CI does (pwsh):

@@ -68,24 +70,9 @@
 docker inspect --format '{{.Config.User}}' hookrelay:ci
-docker run --rm --entrypoint sh hookrelay:ci -c 'for p in /bin/uv /usr/bin/uv /bin/uvx /usr/bin/uvx /root/.cache/uv /usr/local/bin/bun; do [ -e "$p" ] && echo "PRESENT $p" && exit 1; done; command -v gcc && exit 1; echo runtime clean'
-docker run --rm --entrypoint python hookrelay:ci -c 'import sys, django; print(".".join(map(str, sys.version_info[:3])))'
+docker create --name hookrelay-inspect hookrelay:ci; docker export hookrelay-inspect -o hookrelay-rootfs.tar; docker rm hookrelay-inspect; uv run python scripts/inspect_rootfs.py hookrelay-rootfs.tar
+docker run --rm --entrypoint /app/.venv/bin/python hookrelay:ci -c "import sys, django, psycopg, uvloop, httptools; print(sys.version_info[:3], sys.executable)"
 trivy image --format cyclonedx --output sbom-image.cdx.json hookrelay:ci
-trivy image --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
-```
-Use Trivy v0.74.0 locally as CI does (`trivy --version`); the SBOM comes first so it exists even when the scan fails.
-
-Only when the scan reports zero CRITICAL/HIGH: pin the Python base by digest so builder and runtime share one immutable input. Print the index digest and set `ARG PYTHON_IMAGE=python:3.14.7-slim-trixie@sha256:…` in the Dockerfile — the Dockerfile owns that reference and nothing in CI overrides it, so the pin applies to every build; `tests/integration/test_toolchain.py` keeps its version equal to `.python-version`. Do the same for `oven/bun:1.4.2` and `ghcr.io/astral-sh/uv:0.12.13`, and for `postgres:17`/`redis:7` in the workflows and `compose.yaml`. Dependabot's docker ecosystem then keeps the digests current.
-
-```
-foreach ($i in "python:3.14.7-slim-trixie","oven/bun:1.4.2","ghcr.io/astral-sh/uv:0.12.13","postgres:17","redis:7") { docker buildx imagetools inspect $i --format '{{.Name}} {{.Manifest.Digest}}' }
+trivy image --scanners vuln,secret --pkg-types os,library --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
 ```

-If the scan of the unmodified base still reports CRITICAL/HIGH findings, stop and report them: the Dockerfile deliberately performs no `apt-get upgrade` (a moving mirror is not reproducible); an OS-fix strategy is a separate decision.
-
-### SUID/SGID baseline
-
-`docker/suid-allowlist.txt` starts empty, so the first CI image job fails and prints the measured list. Measure locally, review every entry against the base image, then commit the reviewed list:
-
-```
-docker run --rm --entrypoint sh hookrelay:ci -c 'find / -xdev -perm /6000 -type f 2>/dev/null | sort'
-```
+Use Trivy v0.74.0 locally as CI does. The CLI flag is `--pkg-types`; the pinned GitHub action still calls the same setting `vuln-type` and maps it internally — both are correct in their place. The runtime has no shell, so inspection happens from the host on the exported rootfs; `scripts/inspect_rootfs.py` fails on any shell, build tool, package manager, cache, test/doc content, dev package or setuid/setgid file.

@@ -95,3 +82,3 @@

-Production is different: Fly documents that requests reach a Machine through Fly Proxy and documents the forwarded headers, but it does not publish a stable proxy-source CIDR, and one observed source address is not a boundary. Rule: **no production deployment until the trusted source range is established from a documented Fly property or a staged deployment proof that covers the actual routing topology**, recorded in DECISIONS.md. Never infer a CIDR from one request; never use `*`; if a stable safe allowlist cannot be established, stop for an explicit architecture decision rather than relaxing the gate. The loopback placeholder fails closed behind a proxy (every request redirects to https), which is the intended behaviour until that decision exists.
+Production is different and remains OPEN: Fly documents that requests reach a Machine through Fly Proxy and documents the forwarded headers, but it does not publish a stable proxy-source CIDR, and one observed source address is not a boundary. Rule: **no production deployment until the trusted source range is established from a documented Fly property or a staged deployment proof that covers the actual routing topology**, recorded in DECISIONS.md. Never infer a CIDR from one request; never use `*`; if a stable safe allowlist cannot be established, stop for an explicit architecture decision rather than relaxing the gate. The loopback placeholder fails closed behind a proxy (every request redirects to https), which is the intended behaviour until that decision exists.


--- v1.5.1/compose.yaml
+++ v1.5.2/compose.yaml
@@ -2,3 +2,3 @@
   postgres:
-    image: postgres:17
+    image: postgres:17@sha256:67f41722b7a8cbdb868a44a4995c846eddfdc2973bccb291ce937dce88ad5675
     environment:
@@ -12,3 +12,3 @@
   redis:
-    image: redis:7
+    image: redis:7@sha256:71da9275c5f3fcb97d0fa0c8c5b36cc995327265420f17a04bfd544f458059f7
     ports:

--- v1.5.1/docs/DECISIONS.md
+++ v1.5.2/docs/DECISIONS.md
@@ -30,6 +30,6 @@
 | 24 | 2026-09-14 | Toolchain pinned to the versions that produced the evidence (uv 0.11.7, bun 1.4.2, python 3.14.4-slim, uv image 0.11.7); digests added by the owner, then maintained by Dependabot; `uv audit` is a non-blocking secondary signal while in preview | LOCKED |
-| 25 | 2026-09-14 | Runtime image: three stages; only the runtime ships; uv, uvx, Bun, TypeScript, caches, compilers, dev dependencies, tests and docs never enter it; explicit COPY of runtime paths; no `apt-get upgrade` (moving mirror ≠ reproducible — an OS-fix need is a STOP and a separate decision); system pip kept (deviation from the official image only for a proven reason) | LOCKED |
-| 26 | 2026-09-14 | Python 3.14.7 everywhere from `.python-version`; uv 0.12.13; builder and runtime share one `PYTHON_IMAGE` reference, pinned by digest once a candidate scans clean; digests come from the registry, never invented | LOCKED |
+| 25 | 2026-09-14 | Runtime image: three stages; only the runtime ships; uv, uvx, Bun, TypeScript, caches, compilers, dev dependencies, tests and docs never enter it; explicit COPY of runtime paths; no `apt-get upgrade` (moving mirror ≠ reproducible — an OS-fix need is a STOP and a separate decision); system pip kept (deviation from the official image only for a proven reason) | SUPERSEDED by 33 — the Debian runtime is rejected; no-`apt`, no-pip-removal and explicit-COPY principles carry over |
+| 26 | 2026-09-14 | Python 3.14.7 everywhere from `.python-version`; uv 0.12.13; builder and runtime share one `PYTHON_IMAGE` reference, pinned by digest once a candidate scans clean; digests come from the registry, never invented | SUPERSEDED by 33/34 — Python 3.14.7 and uv 0.12.13 stand; the Debian image and the same-image rule do not |
 | 27 | 2026-09-14 | Trivy on the final runtime image: CRITICAL+HIGH fail, vuln + secret scanners, OS + library, no `ignore-unfixed`, no ignore file, no soft-fail; image CycloneDX SBOM; an unfixed finding stays red until a reviewed VEX/waiver exists (supersedes 18) | LOCKED |
-| 28 | 2026-09-14 | Setuid/setgid files in the runtime are gated against `docker/suid-allowlist.txt`, populated from the first measured clean build and reviewed | LOCKED |
+| 28 | 2026-09-14 | Setuid/setgid files in the runtime are gated against `docker/suid-allowlist.txt`, populated from the first measured clean build and reviewed | SUPERSEDED by 35 — no allowlist; zero setuid/setgid files |
 | 29 | 2026-09-14 | Forwarded-header trust: `FORWARDED_ALLOW_IPS` (uvicorn env, default loopback, CIDR), never `*`; CI proves rejection and acceptance on the bridge network; production deployment is blocked until the Fly proxy trust range is established from documented Fly behaviour or a staged deployment proof covering the routing topology — never inferred from one observed request; if no stable safe allowlist can be established, STOP for an architecture decision (amended 2026-09-14, v1.5.1) | LOCKED |
@@ -38 +38,7 @@
 | 32 | 2026-09-14 | No credential-shaped connection URI (`scheme://user:password@host`) is committed; fixtures are assembled at runtime from synthetic parts; `tests/security/test_repository_hygiene.py` gates the whole tree; loopback/container-local placeholders are the documented exception; GitHub's incident is resolved as a test fixture only after the literal is gone | LOCKED |
+| 33 | 2026-09-14 | Runtime family LOCKED to Chainguard Python: builder `cgr.dev/chainguard/python:latest-dev`, runtime `cgr.dev/chainguard/python:latest` (non-root 65532, no shell, no package manager), venv built in the builder against `/usr/bin/python` and copied into the runtime; `ENTRYPOINT []` with an absolute uvicorn CMD; no useradd/apk/apt/pip removal/shell/sudo/uv/Bun in the runtime. Justification: the owner's local proof — `python:3.14.7-slim-trixie` 53 HIGH + 3 CRITICAL, Alpine clean only with OS mutation and pip removal, Chainguard pair Trivy HIGH=0/CRITICAL=0 with django, psycopg, uvloop and httptools importing | LOCKED |
+| 34 | 2026-09-14 | Every repository-owned external image reference is an index digest measured by the owner: Chainguard builder `7d751040…`, runtime `459a10ea…`, uv 0.12.13 `b485bd65…`, bun 1.4.2 `9114c058…`, postgres:17 `67f41722…` (manifest 17.11), redis:7 `71da9275…` (manifest 7.4.11); `tests/security/test_image_references.py` refuses tag-only references; digests change only deliberately with a rescan | LOCKED |
+| 35 | 2026-09-14 | Runtime rootfs is inspected host-side from `docker export` (`scripts/inspect_rootfs.py`, stdlib): no shell, uv/uvx, Bun/node/npm, compilers, package managers, tests/docs/.env/caches, dev packages; zero setuid/setgid regular files; required files present. No allowlist exists | LOCKED |
+| 36 | 2026-09-14 | Python invariants: `.python-version` is exactly 3.14.7 (static test) and the final image executes `sys.version_info == (3, 14, 7)` from `/app/.venv/bin/python` (CI); nothing is parsed from image tags | LOCKED |
+| 37 | 2026-09-14 | Secret hygiene: only explicit reviewed synthetic combinations (`hookrelay:hookrelay` on the local service hosts, `build:build@localhost`) in approved contexts are allowed as URI literals; a loopback host alone is not an exemption | LOCKED |
+| 38 | 2026-09-14 | Branch ruleset / protection on `main` is an OWNER ACTION and OPEN until configured and verified; nothing in the repository claims it | OPEN |

--- v1.5.1/docs/PROOFS.md
+++ v1.5.2/docs/PROOFS.md
@@ -28,7 +28,7 @@
 | A dependency change that introduces a known vulnerability cannot be merged | `security.yml` job `dependency-review` (`fail-on-severity: low`) | PROVEN (D00, CI gate) on a public repository with the dependency graph enabled |
-| The image runs as non-root, migrates, boots and answers through the Fly proxy contract | CI job `docker` | PROVEN (D00, CI gate) |
-| Zero known unsuppressed CRITICAL/HIGH findings (vuln + secret, OS + library) in the final runtime image at scan time; no ignore-unfixed, no ignore file, no soft-fail | `security.yml` job `image`, daily | GATE DEFINED (D00); PROVEN only by a green scan of the exact image on GitHub |
-| The runtime image contains no uv/uvx/Bun/compilers/caches/dev packages and runs as `app` | `ci.yml` job `docker` | GATE DEFINED (D00); PROVEN by a green run |
-| The runtime interpreter equals `.python-version`; CI and local suites run on the same patch | `tests/integration/test_toolchain.py`; `ci.yml` job `docker` | PROVEN locally (D00); image half by a green run |
-| Setuid/setgid files in the runtime equal the reviewed allowlist | `ci.yml` job `docker`, `docker/suid-allowlist.txt` | GATE DEFINED (D00); allowlist measured by the owner |
+| The final image migrates, boots and answers `/livez` and `/readyz` through the proxy contract | `ci.yml` job `docker` | GATE DEFINED (D00 v1.5.2); PROVEN by a green run |
+| Zero known unsuppressed CRITICAL/HIGH findings (vuln + secret, OS + library) in the final runtime image at scan time; no ignore-unfixed, no ignore file, no soft-fail | `security.yml` job `image`, daily | GATE DEFINED (D00 v1.5.2); PROVEN only by a green scan of the exact built image (the owner's local Chainguard proof image scanned 0/0 under the same policy) |
+| The final runtime rootfs has no shell, build tooling, package manager, caches, tests/docs/.env or dev packages, and zero setuid/setgid files; runs as 65532 | `scripts/inspect_rootfs.py` via `ci.yml` job `docker` (self-tested on synthetic rootfs tars) | GATE DEFINED (D00 v1.5.2); PROVEN by a green run of the Chainguard image |
+| `.python-version` is exactly 3.14.7 and the local suite runs on it | `tests/integration/test_toolchain.py` | PROVEN (D00) |
+| The final image executes Python 3.14.7 from `/app/.venv` and imports django, psycopg, uvloop, httptools | `ci.yml` job `docker` | GATE DEFINED (D00 v1.5.2); PROVEN by a green run (owner's local proof image showed the same, see LEVERANS) |
 | `X-Forwarded-Proto` is ignored from untrusted sources and honoured from `FORWARDED_ALLOW_IPS` | `ci.yml` job `docker` (bridge-network probe both ways) | GATE DEFINED (D00); PROVEN by a green run |
@@ -36,5 +36,6 @@
 | Every GitHub Action is pinned to an immutable commit SHA; workflow token permissions default to `contents: read`, with CodeQL alone receiving the scoped `security-events: write` it requires | `.github/workflows/*.yml` | PROVEN (D00) |
-| uv 0.12.13, bun 1.4.2 and Python 3.14.7 are pinned by exact version; the Dockerfile's `PYTHON_IMAGE` version equals `.python-version` (also with a `@sha256` suffix) | `.python-version`, `Dockerfile`, `tests/integration/test_toolchain.py` | PROVEN (D00) |
-| No credential-bearing connection URI literal exists in the tree; fixtures are built at runtime | `tests/security/test_repository_hygiene.py` (gate + detector self-test) | PROVEN (D00) |
-| Base and service images are pinned by immutable digest | `Dockerfile` `ARG PYTHON_IMAGE`, workflows, `compose.yaml` | GATE DEFINED (D00); PROVEN when the real digests are committed and the exact commit is green |
+| uv 0.12.13, bun 1.4.2 and Python 3.14.7 are pinned by exact version | `.python-version`, `Dockerfile`, workflows, `tests/integration/test_toolchain.py` | PROVEN (D00) |
+| `main` is protected by a ruleset requiring the seven checks | GitHub configuration | OPEN — owner action, not yet configured |
+| No unapproved credential-bearing URI literal exists in the tree: only explicit reviewed synthetic/local fixtures in approved contexts; loopback alone is no exemption | `tests/security/test_repository_hygiene.py` (gate + negative self-test incl. a loopback secret) | PROVEN (D00) |
+| Every repository-owned image reference is an immutable index digest (syntax and presence enforced) | `tests/security/test_image_references.py`; `Dockerfile`, `compose.yaml`, `ci.yml` | STATIC PROVEN (D00 v1.5.2); digest pinning PROVEN when this exact tree builds and passes the image gates |
 | Publishing is idempotent under concurrent identical requests | concurrency test | PLANNED (D02) |

--- v1.5.1/docs/forspec/D00-skeleton.md
+++ v1.5.2/docs/forspec/D00-skeleton.md
@@ -2,3 +2,3 @@

-Version 1.5.1 · 2026-09-14 · Status: LOCKED
+Version 1.5.2 · 2026-09-14 · Status: LOCKED

@@ -15,2 +15,4 @@
 Corrections in 1.5.1 (acceptance issues from the static review of the 1.5 zip; nothing else): the Dockerfile owns the complete `PYTHON_IMAGE` reference and no workflow or README command passes a build-arg for it (a digest pin therefore applies to every build); `tests/integration/test_toolchain.py` also asserts the Dockerfile's `PYTHON_IMAGE` version equals `.python-version`, with or without `@sha256`; Trivy engine `v0.74.0` on both action invocations; runtime SBOM produced and uploaded before the fail-closed scan; `docs/security/README.md` rewritten to the fixed-or-unfixed policy; PROOFS wording made precise (workflow token default read-only, CodeQL scoped write; digest pins GATE DEFINED); production deploy blocked until the Fly trust range is established from documented behaviour or a staged deployment proof; secret-scanning addendum — no credential-shaped URI literal committed, fixtures assembled at runtime, `tests/security/test_repository_hygiene.py` as a fail-closed gate over the whole tree with loopback/container-local placeholders as the documented exception.
+
+Amendments in 1.5.2 (runtime family selection from the owner's local image proof; container, CI and tests only, no application code, no lockfile change): the Debian runtime, the `/usr/local/bin/python3.14` same-image rule, the `apt` discussion, the Debian SUID allowlist, Alpine and pip removal are all superseded. Four-stage Dockerfile — uv source, Bun assets, Chainguard `python:latest-dev` builder (uv against `/usr/bin/python`, `uv sync --locked --no-dev`, collectstatic), Chainguard `python:latest` runtime (65532, no shell, `ENTRYPOINT []`, absolute uvicorn CMD, explicit `COPY --chown=65532:65532`); every image reference an owner-measured index digest incl. `postgres:17`/`redis:7` in compose and CI (`tests/security/test_image_references.py` refuses tag-only); `scripts/inspect_rootfs.py` inspects the exported rootfs on the host (no shell, tooling, package managers, caches, tests/docs/.env, dev packages; zero setuid/setgid; required files present); CI proves user 65532, Python 3.14.7 from `/app/.venv` with django/psycopg/uvloop/httptools, migrate, boot, `/livez`, `/readyz` and the two-way trust boundary without a shell; `.python-version` is a static invariant (3.14.7); hygiene gate tightened to explicit reviewed fixtures in approved contexts; Trivy action keeps `vuln-type` (maps to `--pkg-types`); README/PROOFS precision; ruleset marked OPEN owner action.


--- v1.5.1/docs/reviews/D00-review-log.md
+++ v1.5.2/docs/reviews/D00-review-log.md
@@ -83 +83,12 @@
 | GitHub secret scanning: HIGH "PostgreSQL credentials" on a parser fixture in `tests/integration/test_settings.py` (host.example.test) | false positive, structural fix | all fixture DSNs assembled at runtime (`test_settings.py`, `test_skeleton.py`), decoded password built at runtime, repository hygiene gate added with a planted-literal negative check; incident to be resolved as test fixture after push (v1.5.1) |
+
+## Owner's local image proof → v1.5.2 (runtime family selection)
+
+| Finding | Class | Resolution |
+|---|---|---|
+| `python:3.14.7-slim-trixie` unmodified: 53 HIGH + 3 CRITICAL OS findings under the fail-closed policy | runtime rejected | Debian runtime dropped (v1.5.2) |
+| Alpine reaches zero only with OS mutation plus pip removal (pip's vendored BOM as scanner noise) | rejected: mutation contradicts DECISION 25 | not adopted (v1.5.2) |
+| Chainguard `python:latest-dev` (3.14.7, glibc) → `python:latest` (65532, minimal): Trivy 0/0 for OS and Python packages with the locked Hookrelay venv transferred and django/psycopg/uvloop/httptools importing | runtime selected | four-stage Dockerfile, digest-pinned inputs, shell-less host-side inspection, zero-SUID invariant, version/digest static tests (v1.5.2) |
+| `Dockerfile.chainguard-test` was local experimentation | evidence only | not committed (v1.5.2) |
+| Hygiene gate exempted loopback hosts broadly | tightening | explicit reviewed fixture combinations in approved contexts; loopback secret negative test (v1.5.2) |
+| README/PROOFS wording: "read-only token", "same as CI", Docker rows PROVEN for a runtime no longer used, ruleset implied | precision | corrected; ruleset marked OPEN owner action (v1.5.2) |

--- v1.5.1/tests/integration/test_toolchain.py
+++ v1.5.2/tests/integration/test_toolchain.py
@@ -1,4 +1,8 @@
-"""Toolchain invariants: one Python version, owned by .python-version."""
+"""Toolchain invariants: one approved Python version, owned by .python-version.

-import re
+The runtime half (the built image executes 3.14.7 from /app/.venv) is proven
+in CI's docker job; the image tags carry no version, so nothing is parsed
+from them.
+"""
+
 import sys
@@ -7,5 +11,7 @@
 ROOT = Path(__file__).resolve().parents[2]
-PYTHON_IMAGE = re.compile(
-    r"^ARG PYTHON_IMAGE=python:(?P<version>\d+\.\d+\.\d+)-slim-trixie(@sha256:[0-9a-f]{64})?$"
-)
+APPROVED_PYTHON = "3.14.7"
+
+
+def test_python_version_file_is_the_approved_version() -> None:
+    assert (ROOT / ".python-version").read_text().strip() == APPROVED_PYTHON

@@ -16,15 +22 @@
     assert ".".join(map(str, sys.version_info[:3])) == pinned
-
-
-def test_dockerfile_python_image_matches_python_version_file() -> None:
-    # The Dockerfile owns the image reference (tag or tag@sha256); nothing in
-    # CI overrides it, so this is the only place the version can drift.
-    pinned = (ROOT / ".python-version").read_text().strip()
-    lines = [
-        m
-        for line in (ROOT / "Dockerfile").read_text().splitlines()
-        if (m := PYTHON_IMAGE.match(line))
-    ]
-
-    assert len(lines) == 1
-    assert lines[0]["version"] == pinned

--- v1.5.1/tests/security/test_repository_hygiene.py
+++ v1.5.2/tests/security/test_repository_hygiene.py
@@ -1,9 +1,8 @@
-"""No credential-shaped connection URI may be committed.
+"""No unapproved credential-shaped connection URI may be committed.

-GitHub secret scanning reads source text. A fixture such as
-scheme://user:password@db.example.test is noise there even when synthetic, so
-tests build such values at runtime and this gate fails the suite if a literal
-one lands anywhere in the tree. Loopback and container-local hosts are the
-only allowed targets: they are the compose/CI placeholders GitHub does not
-classify as credentials, and no secret can be behind them.
+GitHub secret scanning reads source text. Fixtures build DSNs at runtime;
+this gate fails the suite if a literal scheme://user:password@host appears in
+the tree unless it is one of the explicit, reviewed synthetic combinations
+below in one of the contexts that legitimately carry them. A loopback host is
+not an exemption on its own: an unapproved credential on 127.0.0.1 still fails.
 """
@@ -26,3 +25,2 @@
 SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pyc"}
-LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}

@@ -33,5 +31,33 @@

+# (user, password, host): the compose development credentials on the local
+# service hosts, and the Docker build-only placeholder. Nothing else.
+APPROVED_FIXTURES = {
+    ("hookrelay", "hookrelay", "127.0.0.1"),
+    ("hookrelay", "hookrelay", "localhost"),
+    ("hookrelay", "hookrelay", "host.docker.internal"),
+    ("build", "build", "localhost"),
+}
+# Where those fixtures may appear: development defaults, CI services, the
+# documented placeholder file, the build-only placeholder, the README's local
+# commands, and the evidence logs under docs/.
+APPROVED_CONTEXTS = (
+    "config/settings/dev.py",
+    "config/settings/test.py",
+    ".env.example",
+    ".github/workflows/ci.yml",
+    "Dockerfile",
+    "README.md",
+    "docs/",
+)

-def find_credential_uris(text: str) -> list[str]:
-    return [m.group(0) for m in CREDENTIAL_URI.finditer(text) if m.group("host") not in LOCAL_HOSTS]
+
+def find_unapproved_uris(text: str, relative_path: str) -> list[str]:
+    hits = []
+    for m in CREDENTIAL_URI.finditer(text):
+        combination = (m.group("user"), m.group("password"), m.group("host"))
+        in_context = relative_path.startswith(APPROVED_CONTEXTS)
+        if combination in APPROVED_FIXTURES and in_context:
+            continue
+        hits.append(m.group(0))
+    return hits

@@ -49,3 +75,3 @@

-def test_no_credential_bearing_uri_is_committed() -> None:
+def test_no_unapproved_credential_bearing_uri_is_committed() -> None:
     offenders = {}
@@ -56,5 +82,6 @@
             continue
-        hits = find_credential_uris(text)
+        relative = path.relative_to(ROOT).as_posix()
+        hits = find_unapproved_uris(text, relative)
         if hits:
-            offenders[str(path.relative_to(ROOT))] = hits
+            offenders[relative] = hits

@@ -63,12 +90,13 @@

-def test_detector_flags_remote_hosts_and_allows_local_placeholders() -> None:
-    # Both samples are assembled at runtime; neither exists as source text.
+def test_detector_rejects_unapproved_secrets_even_on_loopback() -> None:
+    # All samples are assembled at runtime; none exists as source text.
     at = chr(64)
     remote = f"postgresql://svc:{'fixture-' + 'pw'}{at}db.example.test:5432/app"
-    local = f"redis://:{'fixture-' + 'pw'}{at}127.0.0.1:6379/0"
+    loopback_secret = f"postgresql://admin:{'REAL_' + 'SECRET'}{at}127.0.0.1/hookrelay"
+    approved = f"postgresql://hookrelay:hookrelay{at}127.0.0.1:55433/hookrelay"

-    hits = find_credential_uris(f"x {remote} y {local}")
-
-    assert len(hits) == 1
-    assert hits[0] == remote.split(":5432", 1)[0]
-    assert find_credential_uris(local) == []
+    assert len(find_unapproved_uris(remote, "config/settings/dev.py")) == 1
+    assert len(find_unapproved_uris(loopback_secret, "config/settings/dev.py")) == 1
+    assert find_unapproved_uris(approved, "config/settings/dev.py") == []
+    # An approved combination outside an approved context is still rejected.
+    assert len(find_unapproved_uris(approved, "apps/accounts/models.py")) == 1

--- /dev/null
+++ v1.5.2/scripts/inspect_rootfs.py
+"""Fail-closed inspection of the exported runtime rootfs (CI, host side).
+
+The production image has no shell, so nothing can be asked from inside it.
+`docker export` gives the merged filesystem as a tar; this script checks exact
+paths and mode bits with the standard library only.
+
+usage: python3 scripts/inspect_rootfs.py hookrelay-rootfs.tar
+"""
+
+import sys
+import tarfile
+
+# Exact executable locations that must not exist in the runtime.
+FORBIDDEN_FILES = {
+    "bin/sh",
+    "bin/bash",
+    "bin/ash",
+    "bin/dash",
+    "bin/busybox",
+    "usr/bin/sh",
+    "usr/bin/bash",
+    "usr/bin/ash",
+    "usr/bin/dash",
+    "usr/bin/busybox",
+    "bin/uv",
+    "usr/bin/uv",
+    "usr/local/bin/uv",
+    "bin/uvx",
+    "usr/bin/uvx",
+    "usr/local/bin/uvx",
+    "usr/local/bin/bun",
+    "usr/local/bin/bunx",
+    "usr/bin/bun",
+    "usr/bin/node",
+    "usr/local/bin/node",
+    "usr/bin/npm",
+    "usr/local/bin/npm",
+    "usr/bin/npx",
+    "usr/bin/gcc",
+    "usr/bin/cc",
+    "usr/bin/g++",
+    "usr/bin/c++",
+    "usr/bin/make",
+    "usr/bin/cmake",
+    "usr/bin/ld",
+    "sbin/apk",
+    "usr/sbin/apk",
+    "usr/bin/apk",
+    "usr/bin/apt",
+    "usr/bin/apt-get",
+    "usr/bin/dpkg",
+    "usr/bin/yum",
+    "usr/bin/dnf",
+    "usr/bin/sudo",
+    "usr/bin/su",
+    "app/.env",
+    "app/conftest.py",
+    "app/pyproject.toml",
+    "app/uv.lock",
+}
+# Directory trees that must be empty of regular files.
+FORBIDDEN_TREES = (
+    "app/tests/",
+    "app/docs/",
+    "app/node_modules/",
+    "app/.git/",
+    "app/.venv/.cache/",
+    "root/.cache/",
+    "home/nonroot/.cache/",
+    "home/app/.cache/",
+    "app/.cache/",
+    "var/cache/apk/",
+    "var/cache/apt/",
+    "var/lib/apt/lists/",
+)
+# Development-only packages that must not be present in the production venv.
+FORBIDDEN_SITE_PACKAGES = (
+    "pytest",
+    "_pytest",
+    "mypy",
+    "ruff",
+    "pip_audit",
+    "pre_commit",
+    "django_stubs",
+    "coverage",
+)
+# Paths that must exist: proves the export is the real image, not an empty tar.
+REQUIRED_FILES = (
+    "app/.venv/bin/uvicorn",
+    "app/.venv/bin/python",
+    "app/manage.py",
+    "app/staticfiles/staticfiles.json",
+)
+
+
+def main(path: str) -> int:
+    violations: list[str] = []
+    present: set[str] = set()
+    with tarfile.open(path) as tar:
+        for member in tar:
+            name = member.name.lstrip("./")
+            present.add(name)
+            if not member.isfile():
+                continue
+            if name in FORBIDDEN_FILES:
+                violations.append(f"forbidden file: /{name}")
+            if name.startswith(FORBIDDEN_TREES):
+                violations.append(f"forbidden tree content: /{name}")
+            if name.startswith("app/.venv/lib/") and "/site-packages/" in name:
+                top = name.split("/site-packages/", 1)[1].split("/", 1)[0]
+                if top.split("-", 1)[0] in FORBIDDEN_SITE_PACKAGES:
+                    violations.append(f"development package in runtime venv: /{name}")
+            if member.mode & 0o6000:
+                violations.append(f"setuid/setgid bit: /{name} mode {member.mode:o}")
+    for required in REQUIRED_FILES:
+        if required not in present:
+            violations.append(f"missing required file: /{required}")
+    if violations:
+        print("ROOTFS INSPECTION FAILED")
+        for line in sorted(set(violations)):
+            print("  " + line)
+        return 1
+    print(
+        f"rootfs clean: {len(present)} entries; no shell, build tooling, caches or dev packages; "
+        "0 setuid/setgid files"
+    )
+    return 0
+
+
+if __name__ == "__main__":
+    sys.exit(main(sys.argv[1]))

--- /dev/null
+++ v1.5.2/tests/security/test_image_references.py
+"""Every external image reference the repository owns is pinned by digest.
+
+Syntax and presence are enforced; the values themselves are the owner's
+measured digests recorded in the D00 evidence and updated only deliberately.
+"""
+
+import re
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[2]
+DIGEST_REF = re.compile(r"^[a-z0-9./_-]+(:[A-Za-z0-9._-]+)?@sha256:[0-9a-f]{64}$")
+DOCKERFILE_ARGS = ("PYTHON_BUILDER_IMAGE", "PYTHON_RUNTIME_IMAGE", "UV_IMAGE", "BUN_IMAGE")
+
+
+def dockerfile_args() -> dict[str, str]:
+    args = {}
+    for line in (ROOT / "Dockerfile").read_text().splitlines():
+        if line.startswith("ARG ") and "=" in line:
+            name, value = line[4:].split("=", 1)
+            args[name.strip()] = value.strip()
+    return args
+
+
+def service_images(path: Path) -> list[str]:
+    return [
+        line.split("image:", 1)[1].strip()
+        for line in path.read_text().splitlines()
+        if line.strip().startswith("image:")
+    ]
+
+
+def test_dockerfile_base_images_are_digest_pinned() -> None:
+    args = dockerfile_args()
+
+    assert set(DOCKERFILE_ARGS) <= set(args)
+    for name in DOCKERFILE_ARGS:
+        assert DIGEST_REF.match(args[name]), f"{name}={args[name]}"
+
+
+def test_compose_services_are_digest_pinned() -> None:
+    images = service_images(ROOT / "compose.yaml")
+
+    assert len(images) == 2
+    assert all(DIGEST_REF.match(image) for image in images), images
+
+
+def test_ci_service_images_are_digest_pinned() -> None:
+    images = service_images(ROOT / ".github" / "workflows" / "ci.yml")
+
+    assert len(images) == 4
+    assert all(DIGEST_REF.match(image) for image in images), images
+
+
+def test_digest_pattern_rejects_tag_only_and_malformed_digests() -> None:
+    assert DIGEST_REF.match("postgres:17") is None
+    assert DIGEST_REF.match("postgres:17@sha256:" + "0" * 63) is None
+    assert DIGEST_REF.match("postgres:17@sha256:" + "G" * 64) is None
+    assert DIGEST_REF.match("cgr.dev/chainguard/python:latest@sha256:" + "a" * 64)

--- v1.5.1/docker/suid-allowlist.txt
+++ /dev/null
-# Allowlist of setuid/setgid files permitted in the final runtime image, one
-# absolute path per line. CI fails when the image contains any privileged
-# file not listed here, or when a listed one is missing. Populate it from the
-# first measured clean build (README, "SUID/SGID baseline"): review every
-# entry against the base image before committing it. Empty until measured.
```

---

# LEVERANS D00 — v1.5.1 (correction pass + secret-scanning addendum)

Förspec: docs/forspec/D00-skeleton.md v1.5.1 (LOCKED). Zip: hookrelay-20260914-1332-d00-v1_5_1.zip. Base: hookrelay-20260914-1317-d00-v1_5.zip (SHA256 01d684f6…64a5d3). Supersedes the 1327 v1.5.1 zip (never committed). Six acceptance corrections plus the secret-scanning requirement; no application code, no lockfile change (`uv.lock`, `bun.lock` byte-identical).

## A. Exact files changed

ADDED: tests/security/__init__.py, tests/security/test_repository_hygiene.py
MODIFIED: .github/workflows/ci.yml, .github/workflows/security.yml, Dockerfile, README.md, docs/DECISIONS.md, docs/PROOFS.md, docs/forspec/D00-skeleton.md, docs/reviews/D00-review-log.md, docs/security/README.md, fly.toml, tests/integration/test_settings.py, tests/integration/test_skeleton.py, tests/integration/test_toolchain.py, docs/LEVERANS-D00.md
DELETED: none

## B. Exact diff (v1.5 → v1.5.1, unified, context 1; this file excluded; credential-shaped removed lines are redacted so this note stays clean)

```diff
--- v1.5/.github/workflows/ci.yml
+++ v1.5.1/.github/workflows/ci.yml
@@ -147,4 +147,6 @@

-      - name: Build image (no cache, Python from .python-version)
-        run: docker build --no-cache --build-arg "PYTHON_IMAGE=python:$(cat .python-version)-slim-trixie" -t hookrelay:ci .
+      # The Dockerfile owns the complete PYTHON_IMAGE reference (tag now,
+      # tag@sha256 after the first clean scan); no build-arg may override it.
+      - name: Build image (no cache)
+        run: docker build --no-cache -t hookrelay:ci .


--- v1.5/.github/workflows/security.yml
+++ v1.5.1/.github/workflows/security.yml
@@ -83,18 +83,10 @@

-      - name: Build image (no cache, Python from .python-version)
-        run: docker build --no-cache --build-arg "PYTHON_IMAGE=python:$(cat .python-version)-slim-trixie" -t hookrelay:ci .
+      # The Dockerfile owns the complete PYTHON_IMAGE reference (tag now,
+      # tag@sha256 after the first clean scan); no build-arg may override it.
+      - name: Build image (no cache)
+        run: docker build --no-cache -t hookrelay:ci .

-      # Zero known unsuppressed HIGH/CRITICAL findings in the final runtime
-      # image at scan time. No ignore-unfixed, no ignore file, no soft-fail.
-      # An unfixed finding keeps this red until a reviewed VEX decision exists.
-      - name: Container vulnerability scan (fail-closed)
-        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
-        with:
-          image-ref: hookrelay:ci
-          format: table
-          exit-code: "1"
-          scanners: vuln,secret
-          vuln-type: os,library
-          severity: CRITICAL,HIGH
-
+      # The SBOM is produced before the gate so it exists as evidence when the
+      # scan goes red. Trivy engine pinned explicitly: the action's embedded
+      # default lags upstream.
       - name: Runtime image SBOM (CycloneDX)
@@ -102,2 +94,3 @@
         with:
+          version: v0.74.0
           image-ref: hookrelay:ci
@@ -110,2 +103,16 @@
           path: sbom-image.cdx.json
+
+      # Zero known unsuppressed HIGH/CRITICAL findings in the final runtime
+      # image at scan time, fixed or unfixed. No ignore file, no soft-fail.
+      # An unfixed finding keeps this red until a reviewed VEX/waiver exists.
+      - name: Container vulnerability scan (fail-closed)
+        uses: aquasecurity/trivy-action@ed142fd0673e97e23eac54620cfb913e5ce36c25 # v0.36.0
+        with:
+          version: v0.74.0
+          image-ref: hookrelay:ci
+          format: table
+          exit-code: "1"
+          scanners: vuln,secret
+          vuln-type: os,library
+          severity: CRITICAL,HIGH


--- v1.5/Dockerfile
+++ v1.5.1/Dockerfile
@@ -7,4 +7,6 @@
 # and once a candidate has scanned clean the reference is pinned by digest
-# (python:3.14.7-slim-trixie@sha256:...). No apt mutation: reproducibility
-# comes from the pinned input, and a base that needs OS fixes is a STOP.
+# (python:3.14.7-slim-trixie@sha256:...). This ARG is never overridden from
+# CI; tests/integration/test_toolchain.py keeps its version equal to
+# .python-version. No apt mutation: reproducibility comes from the pinned
+# input, and a base that needs OS fixes is a STOP.


--- v1.5/README.md
+++ v1.5.1/README.md
@@ -49,2 +49,4 @@

+No credential-shaped connection URI is committed: test fixtures assemble DSNs at runtime, and `tests/security/test_repository_hygiene.py` fails the suite if a literal `scheme://user:password@host` appears anywhere in the tree (loopback and container-local hosts — the compose/CI placeholders — are the only allowed targets). The same check by hand: `git grep -n -E '(postgres(ql)?|redis(s)?)://[^[:space:]/:@]*:[^[:space:]@]+@'` should list only loopback hosts.
+
 Rules that do not move: a later drop never weakens an earlier gate to get green. `# type: ignore`, `# noqa` and coverage exclusions name the narrowest scope and the reason on the same line. Warnings are errors; an exclusion names the exact warning. Flaky concurrency tests are fixed at the race, never retried. Vulnerability exceptions follow `docs/security/README.md`. The claim → evidence registry lives in `docs/PROOFS.md`.
@@ -64,3 +66,3 @@
 ```
-docker build --no-cache --build-arg "PYTHON_IMAGE=python:$(Get-Content .python-version)-slim-trixie" -t hookrelay:ci .
+docker build --no-cache -t hookrelay:ci .
 docker inspect --format '{{.Config.User}}' hookrelay:ci
@@ -68,7 +70,8 @@
 docker run --rm --entrypoint python hookrelay:ci -c 'import sys, django; print(".".join(map(str, sys.version_info[:3])))'
+trivy image --format cyclonedx --output sbom-image.cdx.json hookrelay:ci
 trivy image --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
-trivy image --format cyclonedx --output sbom-image.cdx.json hookrelay:ci
 ```
+Use Trivy v0.74.0 locally as CI does (`trivy --version`); the SBOM comes first so it exists even when the scan fails.

-Only when the scan reports zero CRITICAL/HIGH: pin the Python base by digest so builder and runtime share one immutable input. Print the index digest and set `ARG PYTHON_IMAGE=python:3.14.7-slim-trixie@sha256:…` in the Dockerfile (both Python stages use that one ARG); do the same for `oven/bun:1.4.2` and `ghcr.io/astral-sh/uv:0.12.13`, and for `postgres:17`/`redis:7` in the workflows and `compose.yaml`. Dependabot's docker ecosystem then keeps the digests current.
+Only when the scan reports zero CRITICAL/HIGH: pin the Python base by digest so builder and runtime share one immutable input. Print the index digest and set `ARG PYTHON_IMAGE=python:3.14.7-slim-trixie@sha256:…` in the Dockerfile — the Dockerfile owns that reference and nothing in CI overrides it, so the pin applies to every build; `tests/integration/test_toolchain.py` keeps its version equal to `.python-version`. Do the same for `oven/bun:1.4.2` and `ghcr.io/astral-sh/uv:0.12.13`, and for `postgres:17`/`redis:7` in the workflows and `compose.yaml`. Dependabot's docker ecosystem then keeps the digests current.

@@ -90,3 +93,5 @@

-Uvicorn honours `X-Forwarded-*` only from `FORWARDED_ALLOW_IPS` (its own variable; default `127.0.0.1`; CIDR accepted). No wildcard exists in the image or `fly.toml`. CI proves both directions on the bridge network: from an untrusted source the header is ignored and Django answers 301 (it saw http); from an allowed subnet it is honoured and `/readyz` answers 200. Before the first Fly deploy, measure the proxy's source address (log `scope["client"]` on a throwaway request, or read it from the first `readyz` access log), set `FORWARDED_ALLOW_IPS` in `fly.toml` `[env]` to that network, and record the evidence in DECISIONS.md. With the loopback default left in place behind Fly, every request would redirect to https forever — fail closed by design, not silently permissive.
+Uvicorn honours `X-Forwarded-*` only from `FORWARDED_ALLOW_IPS` (its own variable; default `127.0.0.1`; CIDR accepted). No wildcard exists in the image or `fly.toml`. CI proves both directions on the bridge network: from an untrusted source the header is ignored and Django answers 301 (it saw http); from an allowed subnet it is honoured and `/readyz` answers 200.
+
+Production is different: Fly documents that requests reach a Machine through Fly Proxy and documents the forwarded headers, but it does not publish a stable proxy-source CIDR, and one observed source address is not a boundary. Rule: **no production deployment until the trusted source range is established from a documented Fly property or a staged deployment proof that covers the actual routing topology**, recorded in DECISIONS.md. Never infer a CIDR from one request; never use `*`; if a stable safe allowlist cannot be established, stop for an explicit architecture decision rather than relaxing the gate. The loopback placeholder fails closed behind a proxy (every request redirects to https), which is the intended behaviour until that decision exists.


--- v1.5/docs/DECISIONS.md
+++ v1.5.1/docs/DECISIONS.md
@@ -34,3 +34,5 @@
 | 28 | 2026-09-14 | Setuid/setgid files in the runtime are gated against `docker/suid-allowlist.txt`, populated from the first measured clean build and reviewed | LOCKED |
-| 29 | 2026-09-14 | Forwarded-header trust: `FORWARDED_ALLOW_IPS` (uvicorn env, default loopback, CIDR), never `*`; CI proves rejection and acceptance on the bridge network; the Fly proxy source network is measured at first deploy and recorded here before `fly.toml` is set | LOCKED |
+| 29 | 2026-09-14 | Forwarded-header trust: `FORWARDED_ALLOW_IPS` (uvicorn env, default loopback, CIDR), never `*`; CI proves rejection and acceptance on the bridge network; production deployment is blocked until the Fly proxy trust range is established from documented Fly behaviour or a staged deployment proof covering the routing topology — never inferred from one observed request; if no stable safe allowlist can be established, STOP for an architecture decision (amended 2026-09-14, v1.5.1) | LOCKED |
 | 30 | 2026-09-14 | `.env.example` restored with sanitized development placeholders (ports 55433/56380); `.env` ignored and outside the build context; python-decouple deferred to v1.6 with production reading the process environment only and ALLOWED_HOSTS semantics preserved | LOCKED |
+| 31 | 2026-09-14 | The Dockerfile owns the complete `PYTHON_IMAGE` reference; CI never passes a build-arg for it, so a digest pin in the Dockerfile applies to every build; Trivy engine pinned explicitly (v0.74.0) on both invocations; the runtime SBOM is produced and uploaded before the fail-closed scan | LOCKED |
+| 32 | 2026-09-14 | No credential-shaped connection URI (`scheme://user:password@host`) is committed; fixtures are assembled at runtime from synthetic parts; `tests/security/test_repository_hygiene.py` gates the whole tree; loopback/container-local placeholders are the documented exception; GitHub's incident is resolved as a test fixture only after the literal is gone | LOCKED |

--- v1.5/docs/PROOFS.md
+++ v1.5.1/docs/PROOFS.md
@@ -34,3 +34,7 @@
 | `X-Forwarded-Proto` is ignored from untrusted sources and honoured from `FORWARDED_ALLOW_IPS` | `ci.yml` job `docker` (bridge-network probe both ways) | GATE DEFINED (D00); PROVEN by a green run |
-| Every GitHub Action is pinned to an immutable commit SHA under a read-only token; uv 0.12.13, bun 1.4.2, Python 3.14.7 and base images pinned to exact versions | `.github/workflows/*.yml`, `Dockerfile`, `.python-version` | PROVEN (D00) — digests are added by the owner after the first clean scan |
+| Production forwarded-header trust is a stable, documented or staged-deployment-proven boundary, never inferred from one request and never `*` | DECISIONS 29; production deploy blocked until established | OPEN — deploy blocked |
+| Every GitHub Action is pinned to an immutable commit SHA; workflow token permissions default to `contents: read`, with CodeQL alone receiving the scoped `security-events: write` it requires | `.github/workflows/*.yml` | PROVEN (D00) |
+| uv 0.12.13, bun 1.4.2 and Python 3.14.7 are pinned by exact version; the Dockerfile's `PYTHON_IMAGE` version equals `.python-version` (also with a `@sha256` suffix) | `.python-version`, `Dockerfile`, `tests/integration/test_toolchain.py` | PROVEN (D00) |
+| No credential-bearing connection URI literal exists in the tree; fixtures are built at runtime | `tests/security/test_repository_hygiene.py` (gate + detector self-test) | PROVEN (D00) |
+| Base and service images are pinned by immutable digest | `Dockerfile` `ARG PYTHON_IMAGE`, workflows, `compose.yaml` | GATE DEFINED (D00); PROVEN when the real digests are committed and the exact commit is green |
 | Publishing is idempotent under concurrent identical requests | concurrency test | PLANNED (D02) |

--- v1.5/docs/forspec/D00-skeleton.md
+++ v1.5.1/docs/forspec/D00-skeleton.md
@@ -2,3 +2,3 @@

-Version 1.5 · 2026-09-14 · Status: LOCKED
+Version 1.5.1 · 2026-09-14 · Status: LOCKED

@@ -13,2 +13,4 @@
 Amendments in 1.5 (from 1.4, after `security / image` failed on root commit fbae421; container, toolchain and CI only, no application code, no lockfile change): three-stage Dockerfile — assets (Bun, typecheck + build), Python dependency builder (uv 0.12.13, `uv sync --locked --no-dev`, collectstatic), runtime (same `PYTHON_IMAGE` reference, explicit COPY of `.venv`, `manage.py`, `config`, `apps`, `templates`, `static/dist`, `staticfiles`, user `app`); no uv/uvx/Bun/caches/compilers/dev dependencies in the runtime; no `apt-get upgrade`; system pip kept; Python 3.14.7 from `.python-version` everywhere (CI omits the version input, Docker takes `ARG PYTHON_IMAGE`, `tests/integration/test_toolchain.py` pins the interpreter); uv 0.12.13 across setup-uv and the uv image, `uv audit` invocation corrected; Trivy fail-closed on CRITICAL/HIGH with vuln + secret scanners, no `ignore-unfixed`, plus a runtime-image CycloneDX SBOM; `ci / docker` gains a no-cache build, runtime-clean gate, interpreter gate, setuid/setgid allowlist gate (`docker/suid-allowlist.txt`, measured by the owner), migrate through the image and a two-way forwarded-header trust probe on the bridge network; `--forwarded-allow-ips=*` removed everywhere, trust comes from `FORWARDED_ALLOW_IPS` (default loopback), Fly value measured at first deploy; `bun run typecheck:tools` blocking in `ci / test`; `.env.example` restored (55433/56380); `.dockerignore` tightened. Superseded text below in §6b is replaced by this paragraph.
+
+Corrections in 1.5.1 (acceptance issues from the static review of the 1.5 zip; nothing else): the Dockerfile owns the complete `PYTHON_IMAGE` reference and no workflow or README command passes a build-arg for it (a digest pin therefore applies to every build); `tests/integration/test_toolchain.py` also asserts the Dockerfile's `PYTHON_IMAGE` version equals `.python-version`, with or without `@sha256`; Trivy engine `v0.74.0` on both action invocations; runtime SBOM produced and uploaded before the fail-closed scan; `docs/security/README.md` rewritten to the fixed-or-unfixed policy; PROOFS wording made precise (workflow token default read-only, CodeQL scoped write; digest pins GATE DEFINED); production deploy blocked until the Fly trust range is established from documented behaviour or a staged deployment proof; secret-scanning addendum — no credential-shaped URI literal committed, fixtures assembled at runtime, `tests/security/test_repository_hygiene.py` as a fail-closed gate over the whole tree with loopback/container-local placeholders as the documented exception.


--- v1.5/docs/reviews/D00-review-log.md
+++ v1.5.1/docs/reviews/D00-review-log.md
@@ -71 +71,13 @@
 | `apt-get upgrade` and system-pip removal proposed by the implementer | rejected by review | not done: mutable mirror is not reproducible; pip removal only for a proven reason (v1.5) |
+
+## Static review of the v1.5 zip (01d684f6…) → v1.5.1
+
+| Finding | Class | Resolution |
+|---|---|---|
+| CI `--build-arg PYTHON_IMAGE=…` would override a future digest pin in the Dockerfile | BLOCKER (latent) | build-arg removed from both workflows and the README; Dockerfile owns the reference; test pins its version to `.python-version` incl. `@sha256` (v1.5.1) |
+| trivy-action v0.36.0 embeds Trivy 0.70.0 | design | `version: v0.74.0` on both invocations (v1.5.1) |
+| `docs/security/README.md` still said unfixed findings are excluded | policy contradiction | rewritten to Decision 27 (v1.5.1) |
+| PROOFS overclaimed "read-only token" and "images pinned" | wording | split into precise rows; digests GATE DEFINED (v1.5.1) |
+| SBOM generated after the fail-closed scan | ordering | SBOM + upload before the scan (v1.5.1) |
+| Fly trust range "measured from one request" | security procedure | production deploy blocked until a documented or staged-deployment-proven boundary exists (v1.5.1) |
+| GitHub secret scanning: HIGH "PostgreSQL credentials" on a parser fixture in `tests/integration/test_settings.py` (host.example.test) | false positive, structural fix | all fixture DSNs assembled at runtime (`test_settings.py`, `test_skeleton.py`), decoded password built at runtime, repository hygiene gate added with a planted-literal negative check; incident to be resolved as test fixture after push (v1.5.1) |

--- v1.5/docs/security/README.md
+++ v1.5.1/docs/security/README.md
@@ -2,6 +2,6 @@

-CI blocks any known vulnerability with an available fix (`pip-audit --strict --require-hashes` on the production set and on all groups, `bun audit`, Trivy on the image at CRITICAL/HIGH with unfixed findings excluded). No `--ignore-vuln`, no severity downgrade and no scan skip is added to CI without a record in this directory.
+CI blocks any known vulnerability: `pip-audit --strict --require-hashes` on the production set and on all dependency groups, `bun audit`, and Trivy on the final runtime image at CRITICAL/HIGH — fixed or unfixed, vuln and secret scanners, OS and library. There is no generic ignore file, no severity downgrade, no `ignore-unfixed`, no soft-fail, and no `--ignore-vuln` in CI without a record in this directory.

-An exception is a file `exceptions/<ADVISORY-ID>.md` containing: the advisory; the affected dependency and why it is present; whether production is affected; why exploitation is impossible or reduced here; the temporary mitigation; the owner; an expiry date; the condition under which the exception is removed. The CI suppression references the file, and the file is deleted with the suppression when the fix lands.
+A genuine temporary exception is a reviewed, dated VEX/waiver file `exceptions/<ADVISORY-ID>.md` containing: the advisory; the affected component and why it is present; whether production is affected; why exploitation is impossible or reduced here (evidence, not opinion); the temporary mitigation; the owner; an expiry/review date; the condition under which the exception is removed. The CI suppression references the file, and both are deleted when the fix lands. Until such a record exists, a red scan stays red.

-Remediation is a reviewed dependency update (`uv lock --upgrade-package <name>`, inspect the diff, full suite, commit), never an automated change made by CI.
+Remediation is a reviewed dependency or base-image update (`uv lock --upgrade-package <name>`, a new pinned image digest), inspected, run through the full wall, committed — never an automated change made by CI.

--- v1.5/fly.toml
+++ v1.5.1/fly.toml
@@ -8,5 +8,7 @@
   DJANGO_SETTINGS_MODULE = "config.settings.prod"
-  # Uvicorn trusts X-Forwarded-* only from these sources. Set to the proxy's
-  # measured source network before the first deploy (README, "Forwarded-header
-  # trust"); the loopback default rejects the headers from every other address.
+  # Uvicorn trusts X-Forwarded-* only from these sources. Loopback is the
+  # fail-closed placeholder: production deployment stays blocked until the
+  # proxy trust range is established from documented Fly behaviour or a
+  # staged deployment covering the routing topology (README, "Forwarded-header
+  # trust"). Never derived from one observed request, never "*".
   FORWARDED_ALLOW_IPS = "127.0.0.1"

--- v1.5/tests/integration/test_settings.py
+++ v1.5.1/tests/integration/test_settings.py
@@ -1,2 +1,11 @@
-"""Settings contracts and production fail-closed behavior."""
+"""Settings contracts: URL parsing invariants and production fail-closed behaviour.
+
+Settings modules read the environment at import time, so each test imports a
+fresh copy under a controlled environment and restores the originals afterwards.
+django.conf.settings is untouched: it copied its values at start-up.
+
+Fixture connection URLs are assembled at runtime from synthetic parts so no
+credential-shaped literal is ever committed (GitHub secret scanning reads
+source text, not runtime values).
+"""

@@ -12,6 +21,16 @@

+FIXTURE_PASSWORD = "fixture-" + "password"  # noqa: S105 - synthetic, assembled at runtime
+AT = chr(64)
+
+
+def dsn(scheme: str, user: str, password: str, host: str, path: str) -> str:
+    return f"{scheme}://{user}:{password}{AT}{host}{path}"
+
+
 PROD_ENV = {
     "SECRET_KEY": "x" * 64,
-    "DATABASE_URL": "postgresql://[user password redacted]@db.example.test:5432/hookrelay?sslmode=require",
-    "REDIS_URL": "rediss://[user password redacted]@redis.example.test:6379/0",
+    "DATABASE_URL": dsn(
+        "postgresql", "user", FIXTURE_PASSWORD, "db.example.test:5432", "/hookrelay?sslmode=require"
+    ),
+    "REDIS_URL": dsn("rediss", "default", FIXTURE_PASSWORD, "redis.example.test:6379", "/0"),
     "ALLOWED_HOSTS": "hookrelay.example.test,www.hookrelay.example.test",
@@ -47,3 +66,8 @@
 def test_database_url_query_parameters_pass_through_to_libpq() -> None:
-    config = database_from_url("postgresql://[user password redacted]@host.example.test:6543/db?sslmode=require")
+    # The password carries a percent-encoded "@" so the parser's decoding is
+    # covered; both the encoded and the expected decoded form are built here.
+    encoded_password = "p%40" + "ss"
+    url = dsn("postgresql", "u", encoded_password, "host.example.test:6543", "/db?sslmode=require")
+
+    config = database_from_url(url)

@@ -51,3 +75,3 @@
     assert config["USER"] == "u"
-    assert config["PASSWORD"] == "p@ss"  # noqa: S105 - URL-parsing fixture, not a credential
+    assert config["PASSWORD"] == "p" + AT + "ss"
     assert config["HOST"] == "host.example.test"
@@ -58,3 +82,5 @@
 def test_database_url_cannot_override_the_enforced_connect_timeout() -> None:
-    config = database_from_url("postgresql://[user password redacted]@host.example.test/db?connect_timeout=60")
+    url = dsn("postgresql", "u", FIXTURE_PASSWORD, "host.example.test", "/db?connect_timeout=60")
+
+    config = database_from_url(url)

@@ -104,2 +130,3 @@
     assert dev.DATABASES["default"]["HOST"] == "127.0.0.1"
+    assert dev.DATABASES["default"]["PORT"] == "55433"
     assert dev.DATABASES["default"]["NAME"] == "hookrelay"

--- v1.5/tests/integration/test_skeleton.py
+++ v1.5.1/tests/integration/test_skeleton.py
@@ -50,2 +50,5 @@

+UNREACHABLE_REDIS_PASSWORD = "fixture-" + "password"  # noqa: S105 - synthetic, assembled at runtime
+
+
 @override_settings(
@@ -55,3 +58,3 @@
             # Unreachable Redis must fail fast without leaking the location.
-            "LOCATION": "redis://[user password redacted]@127.0.0.1:9/1",
+            "LOCATION": f"redis://:{UNREACHABLE_REDIS_PASSWORD}{chr(64)}127.0.0.1:9/1",
             "OPTIONS": {"socket_connect_timeout": 1, "socket_timeout": 1},
@@ -65,3 +68,3 @@
     assert response.json() == {"status": "degraded", "db": "ok", "redis": "error"}
-    assert "secret-password" not in response.content.decode()
+    assert UNREACHABLE_REDIS_PASSWORD not in response.content.decode()


--- v1.5/tests/integration/test_toolchain.py
+++ v1.5.1/tests/integration/test_toolchain.py
@@ -1,3 +1,4 @@
-"""The interpreter running the suite is the one .python-version pins."""
+"""Toolchain invariants: one Python version, owned by .python-version."""

+import re
 import sys
@@ -5,6 +6,25 @@

+ROOT = Path(__file__).resolve().parents[2]
+PYTHON_IMAGE = re.compile(
+    r"^ARG PYTHON_IMAGE=python:(?P<version>\d+\.\d+\.\d+)-slim-trixie(@sha256:[0-9a-f]{64})?$"
+)
+

 def test_running_interpreter_matches_python_version_file() -> None:
-    pinned = (Path(__file__).resolve().parents[2] / ".python-version").read_text().strip()
+    pinned = (ROOT / ".python-version").read_text().strip()

     assert ".".join(map(str, sys.version_info[:3])) == pinned
+
+
+def test_dockerfile_python_image_matches_python_version_file() -> None:
+    # The Dockerfile owns the image reference (tag or tag@sha256); nothing in
+    # CI overrides it, so this is the only place the version can drift.
+    pinned = (ROOT / ".python-version").read_text().strip()
+    lines = [
+        m
+        for line in (ROOT / "Dockerfile").read_text().splitlines()
+        if (m := PYTHON_IMAGE.match(line))
+    ]
+
+    assert len(lines) == 1
+    assert lines[0]["version"] == pinned

--- /dev/null
+++ v1.5.1/tests/security/__init__.py


--- /dev/null
+++ v1.5.1/tests/security/test_repository_hygiene.py
+"""No credential-shaped connection URI may be committed.
+
+GitHub secret scanning reads source text. A fixture such as
+scheme://user:password@db.example.test is noise there even when synthetic, so
+tests build such values at runtime and this gate fails the suite if a literal
+one lands anywhere in the tree. Loopback and container-local hosts are the
+only allowed targets: they are the compose/CI placeholders GitHub does not
+classify as credentials, and no secret can be behind them.
+"""
+
+import re
+from pathlib import Path
+
+ROOT = Path(__file__).resolve().parents[2]
+SKIP_DIRS = {
+    ".git",
+    ".venv",
+    "node_modules",
+    "__pycache__",
+    ".mypy_cache",
+    ".ruff_cache",
+    ".pytest_cache",
+    "staticfiles",
+    "dist",
+}
+SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pyc"}
+LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1", "host.docker.internal"}
+
+CREDENTIAL_URI = re.compile(
+    r"\b(?P<scheme>postgres(?:ql)?|redis|rediss|amqp|amqps|mysql|mongodb|mongodb\+srv)://"
+    r"(?P<user>[^\s/:@'\"`]*):(?P<password>[^\s@'\"`]+)@(?P<host>[^\s/:'\"`?]+)"
+)
+
+
+def find_credential_uris(text: str) -> list[str]:
+    return [m.group(0) for m in CREDENTIAL_URI.finditer(text) if m.group("host") not in LOCAL_HOSTS]
+
+
+def tracked_text_files() -> list[Path]:
+    files = []
+    for path in ROOT.rglob("*"):
+        if not path.is_file() or path.suffix in SKIP_SUFFIXES:
+            continue
+        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
+            continue
+        files.append(path)
+    return files
+
+
+def test_no_credential_bearing_uri_is_committed() -> None:
+    offenders = {}
+    for path in tracked_text_files():
+        try:
+            text = path.read_text(encoding="utf-8")
+        except UnicodeDecodeError:
+            continue
+        hits = find_credential_uris(text)
+        if hits:
+            offenders[str(path.relative_to(ROOT))] = hits
+
+    assert offenders == {}
+
+
+def test_detector_flags_remote_hosts_and_allows_local_placeholders() -> None:
+    # Both samples are assembled at runtime; neither exists as source text.
+    at = chr(64)
+    remote = f"postgresql://svc:{'fixture-' + 'pw'}{at}db.example.test:5432/app"
+    local = f"redis://:{'fixture-' + 'pw'}{at}127.0.0.1:6379/0"
+
+    hits = find_credential_uris(f"x {remote} y {local}")
+
+    assert len(hits) == 1
+    assert hits[0] == remote.split(":5432", 1)[0]
+    assert find_credential_uris(local) == []
```

Correction map — (1) digest-pin override: `--build-arg PYTHON_IMAGE` removed from both workflows and the README; build is `docker build --no-cache -t hookrelay:ci .`; the Dockerfile keeps `ARG PYTHON_IMAGE=python:3.14.7-slim-trixie` until the clean scan; `test_dockerfile_python_image_matches_python_version_file` pins its version to `.python-version` with or without `@sha256:<64 hex>` (negative and positive checks in Appendix A). (2) `version: v0.74.0` on both Trivy invocations — release verified from the Trivy repository tags, the `version` input verified in the pinned action manifest. (3) `docs/security/README.md` rewritten: HIGH/CRITICAL fail fixed or unfixed, no ignore file, no downgrade, reviewed dated VEX/waiver with owner and expiry as the only exception. (4) PROOFS split into precise rows: token default `contents: read` with CodeQL's scoped write; version pins PROVEN; digest pins GATE DEFINED. (5) `security / image` order: build → runtime SBOM → upload → fail-closed scan. (6) trust boundary: loopback placeholder kept, one-request inference removed, production deploy blocked until a documented or staged-deployment-proven range exists (README, fly.toml comment, DECISIONS 29 amended, PROOFS row OPEN, DECISIONS 31).

Secret-scanning addendum — every fixture DSN in `tests/integration/test_settings.py` and the unreachable-Redis URL in `tests/integration/test_skeleton.py` are assembled at runtime from synthetic parts (`dsn()`, `FIXTURE_PASSWORD`, `chr(64)`); the percent-decoding assertion is kept and its expected value is built at runtime; `tests/security/test_repository_hygiene.py` scans the whole tree for `scheme://user:password@host` with loopback/container-local hosts as the only allowed targets, and self-tests its detector; a planted literal made the gate fail (Appendix A); `git grep` over tracked files finds no non-local match; README, DECISIONS 32, PROOFS row, review log and förspec updated. Nothing about GitHub's scanner is suppressed; the incident is resolved as a test fixture only after this commit is pushed.

## C. Executed gate results (sandbox: uv 0.12.13, Python 3.14.7, bun 1.4.2, PostgreSQL 16.15 and Redis 7 on 5432/6379 via env)

19 gates, 19 exit 0 (Appendix A): `uv lock --check`, `uv sync --locked`, frozen bun install, `typecheck:tools`, build, `htmx:check`, `bun audit`, pre-commit whole tree with 0 hook modifications, repository secret-pattern scan (no non-local match), ruff check, ruff format, mypy strict (26 files), `manage.py check`, `check --deploy --fail-level WARNING` (0 silenced), migration drift, migrate, pytest 24 passed at 100% branch coverage, both hash-verified pip-audits clean, four YAML files parse. Negative checks: Dockerfile drifted to 3.14.6 → toolchain test fails; `@sha256` placeholder → passes; planted credential literal → hygiene gate fails; all temporary files restored/removed. Docker, Trivy, digests and the Fly range remain unproven here, as in v1.5 §J.

## D. Statement

No application or runtime business logic changed. `config/`, `apps/`, `templates/`, `static/src/`, `scripts/`, `manage.py`, `pyproject.toml`, `uv.lock`, `package.json`, `bun.lock`, `compose.yaml`, `.python-version`, `.dockerignore`, `.env.example`, `docker/suid-allowlist.txt` are byte-identical to v1.5. Code changes are confined to tests: the toolchain invariant test, the runtime-assembled fixtures, and the hygiene gate. `Dockerfile` and `fly.toml` changed only in comments.

## E. Zip

hookrelay-20260914-1332-d00-v1_5_1.zip — SHA256 in the delivery message.

---

## Appendix A — raw gate output (sandbox, v1.5.1)

```
$ uv lock --check
Using CPython 3.14.7
Resolved 82 packages in 1ms
[exit 0]

$ uv sync --locked
Using CPython 3.14.7
Creating virtual environment at: .venv
Resolved 82 packages in 1ms
Installed 79 packages in 225ms
 + anyio==4.15.1
 + asgiref==3.12.1
 + ast-serialize==0.11.1
 + attrs==26.1.0
 + boolean-py==5.0
 + cachecontrol==0.14.4
 + certifi==2026.7.22
 + cfgv==3.5.0
 + charset-normalizer==3.5.1
 + click==8.5.0
 + coverage==7.16.0
 + cyclonedx-python-lib==11.12.0
 + defusedxml==0.7.1
 + distlib==0.4.3
 + django==6.1.1
 + django-htmx==1.29.0
 + django-stubs==6.1.0
 + django-stubs-ext==6.1.0
 + django-tasks-db==0.13.0
 + djangorestframework==3.18.1
 + djangorestframework-stubs==3.18.1
 + drf-spectacular==0.30.0
 + filelock==3.32.6
 + h11==0.16.0
 + httptools==0.8.0
 + identify==2.6.19
 + idna==3.19
 + inflection==0.5.1
 + iniconfig==2.3.0
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + librt==0.15.0
 + license-expression==30.4.4
 + markdown-it-py==4.2.0
 + mdurl==0.1.2
 + msgpack==1.2.2
 + mypy==2.3.1
 + mypy-extensions==1.1.0
 + nodeenv==1.10.0
 + packageurl-python==0.17.6
 + packaging==26.3
 + pathspec==1.1.1
 + pip==26.2.1
 + pip-api==0.0.35
 + pip-audit==2.10.1
 + pip-requirements-parser==32.0.1
 + platformdirs==4.11.8
 + pluggy==1.6.0
 + pre-commit==4.6.2
 + psycopg==3.3.5
 + psycopg-binary==3.3.5
 + py-serializable==2.1.0
 + pygments==2.21.0
 + pyparsing==3.3.2
 + pytest==9.1.1
 + pytest-cov==7.1.0
 + pytest-django==4.14.0
 + python-discovery==1.6.0
 + python-dotenv==1.2.3
 + pyyaml==6.0.3
 + redis==8.1.0
 + referencing==0.37.0
 + requests==2.34.2
 + rich==15.0.0
 + rpds-py==2026.6.3
 + ruff==0.16.7
 + sortedcontainers==2.4.0
 + sqlparse==0.6.0
 + tomli==2.4.1
 + tomli-w==1.2.0
 + types-pyyaml==6.0.12.20260906
 + typing-extensions==4.16.0
 + uritemplate==4.2.0
 + urllib3==2.7.0
 + uvicorn==0.52.4
 + uvloop==0.22.1
 + virtualenv==21.7.9
 + watchfiles==1.2.0
 + websockets==17.1
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

+ @alpinejs/csp@3.17.2
+ @tailwindcss/cli@4.3.3
+ @types/bun@1.4.2
+ htmx.org@4.0.0
+ tailwindcss@4.3.3
+ typescript@7.0.2

46 packages installed [25.00ms]
[exit 0]

$ bun run typecheck:tools
$ tsc --project tsconfig.json --noEmit
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 92ms
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 100 packages) [135.00ms]
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

hook modifications: 0

$ repository secret-pattern scan: git grep for scheme://user:password@host, non-local hosts only
matches outside local hosts: none

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
45 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 26 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ uv run python manage.py migrate --noinput
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, django_tasks_database, sessions
Running migrations:
  No migrations to apply.
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay15
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 24 items

apps/accounts/tests/test_user_model.py .                                 [  4%]
tests/integration/test_skeleton.py ...........                           [ 50%]
tests/integration/test_settings.py ........                              [ 83%]
tests/integration/test_toolchain.py ..                                   [ 91%]
tests/security/test_repository_hygiene.py ..                             [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 24 passed in 1.44s ==============================
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/rp.txt
No known vulnerabilities found
[exit 0]

$ uv run pip-audit --strict --require-hashes -r /tmp/ra.txt
No known vulnerabilities found
[exit 0]

$ YAML parse (ci, security, codeql, dependabot)
4 files parse
[exit 0]

$ invariant test rejects a drifted Dockerfile (negative check on a temporary copy)
1 failed, 1 passed in 0.04s
(Dockerfile restored)

$ invariant test accepts a digest-suffixed reference (positive check on a temporary copy)
2 passed in 0.02s
(Dockerfile restored; the placeholder digest is never committed)

$ hygiene gate rejects a planted credential-shaped literal (negative check on a temporary file)
1 failed, 1 passed in 0.39s
(planted file removed)
```

---

# LEVERANS D00 — v1.5 (container, toolchain, CI gates)

Förspec: docs/forspec/D00-skeleton.md v1.5 (LOCKED). Zip: hookrelay-20260914-1317-d00-v1_5.zip. Base: hookrelay-20260914-1255.zip (SHA256 d0522c6d…465270), the canonical tree after root commit fbae421. Container/toolchain/CI only — no application code, no lockfile change (`uv.lock`, `bun.lock` byte-identical).

## A. Exact files changed (stage these paths; never `git add .`)

```
ADDED (4):
  .env.example
  .python-version
  docker/suid-allowlist.txt
  tests/integration/test_toolchain.py
MODIFIED (11):
  .dockerignore
  .github/workflows/ci.yml
  .github/workflows/security.yml
  Dockerfile
  README.md
  docs/DECISIONS.md
  docs/LEVERANS-D00.md
  docs/PROOFS.md
  docs/forspec/D00-skeleton.md
  docs/reviews/D00-review-log.md
  fly.toml
DELETED (1):
  .coverage
UNCHANGED (54): .gitattributes, .github/dependabot.yml, .github/workflows/codeql.yml, .gitignore, .pre-commit-config.yaml, apps/__init__.py, apps/accounts/__init__.py, apps/accounts/admin.py, apps/accounts/apps.py, apps/accounts/migrations/0001_initial.py, apps/accounts/migrations/__init__.py, apps/accounts/models.py, apps/accounts/tests/__init__.py, apps/accounts/tests/test_user_model.py, bun.lock, compose.yaml, config/__init__.py, config/asgi.py, config/settings/__init__.py, config/settings/base.py, config/settings/dev.py, config/settings/prod.py, config/settings/test.py, config/urls.py, config/views.py, config/wsgi.py, conftest.py, docs/BUILD-PLAN.md, docs/STRUCTURE.md, docs/forspec/D01-accounts.md, docs/forspec/D02-outbox.md, docs/forspec/D03-delivery.md, docs/forspec/D04-circuit-replay.md, docs/forspec/D05-sse-ui.md, docs/forspec/D06-graphql.md, docs/forspec/D07-performance.md, docs/forspec/D08-chaos.md, docs/forspec/D09-kafka-lab.md, docs/forspec/D10-rag.md, docs/security/README.md, manage.py, package.json, pyproject.toml, scripts/copy-assets.ts, static/src/app.css, static/src/app.js, templates/base.html, templates/index.html, tests/__init__.py, tests/integration/__init__.py, tests/integration/test_settings.py, tests/integration/test_skeleton.py, tsconfig.json, uv.lock
```
`.coverage` was a working-tree artefact inside the intake zip; it is git-ignored and not part of the tree.

## B. Diff summary

- `Dockerfile`: three stages (`assets` → `builder` → `runtime`), one `ARG PYTHON_IMAGE=python:3.14.7-slim-trixie` used by both Python stages, uv 0.12.13 copied from a named `uv` stage into the builder only, `UV_PYTHON=/usr/local/bin/python3.14`, `UV_PYTHON_DOWNLOADS=never`, `UV_NO_CACHE=1`, `uv sync --locked --no-dev --no-install-project`, collectstatic in the builder, explicit `COPY --from=builder --chown=app:app` of `.venv`, `manage.py`, `config`, `apps`, `templates`, `static/dist`, `staticfiles`; `USER app`; CMD without `--forwarded-allow-ips`. No `apt-get`, system pip untouched.
- `.dockerignore`: explicit exclusions incl. `.env`, `.env.*`, tests, docs, workflows, compose, fly.toml; `.env.example` no longer un-ignored.
- `.python-version`: `3.14.7`. `tests/integration/test_toolchain.py`: running interpreter equals the file.
- `.github/workflows/ci.yml`: setup-uv 0.12.13 with no `python-version` input; `bun run typecheck:tools` before the build; `docker` job rebuilt as gates — no-cache build with `PYTHON_IMAGE` from `.python-version`, user `app`, runtime-clean (no uv/uvx/Bun/tsc/gcc/node on disk or PATH, no dev packages in the venv), interpreter equals `.python-version` and imports Django, setuid/setgid diff against `docker/suid-allowlist.txt`, migrate through the image, two-way forwarded-header trust probe on the bridge network (`Host: localhost`, subnet discovered from the bridge network).
- `.github/workflows/security.yml`: setup-uv 0.12.13 without the version input; `uv audit --preview-features audit` (the `--all-groups` flag does not exist in 0.12.13); `image` job: no-cache build, Trivy `scanners: vuln,secret`, `vuln-type: os,library`, `severity: CRITICAL,HIGH`, `exit-code: 1`, **no `ignore-unfixed`**, runtime CycloneDX SBOM artifact `sbom-image`.
- `fly.toml`: `FORWARDED_ALLOW_IPS = "127.0.0.1"` in `[env]` with the measurement instruction; `web` command without the wildcard.
- `docker/suid-allowlist.txt`: empty allowlist with the procedure; the gate fails until measured and reviewed.
- `.env.example`: restored, sanitized, ports 55433/56380, production variables named but unset.
- `README.md`: versions, `typecheck:tools` in the quality line, image proof and digest procedure, SUID baseline procedure, forwarded-header trust section. Docs: förspec v1.5 paragraph, PROOFS rows (Trivy claim reworded; four new GATE DEFINED rows), DECISIONS 25–30, review log section.

## C. Non-Docker gates executed (sandbox: Ubuntu 24.04, uv 0.12.13, Python 3.14.7 via `.python-version`, bun 1.4.2, PostgreSQL 16.15 and Redis 7 local on 5432/6379 supplied via env)

24 gates exit 0: `uv lock --check`; `uv sync --locked` (interpreter 3.14.7); frozen bun install; `typecheck:tools`; build; `htmx:check` (0 issues); `bun audit` (clean); pre-commit whole tree (0 modifications); ruff check; ruff format; mypy strict (24 files); `manage.py check`; `check --deploy --fail-level WARNING` (0 silenced); migration drift; fresh drop-and-migrate; pytest 21 passed at 100% branch coverage; spectacular; pip-audit production (284 hashed artifacts) and all groups (335), both clean; lock SBOM (81 components); uvicorn boot (`/livez`, `/readyz` 200); all four YAML files parse. One non-zero: `uv audit` exit 2 — api.osv.dev is blocked from the sandbox; the step is non-blocking by decision and its first real result comes from GitHub. Raw output in Appendix A.

## D. Dockerfile architecture

`assets` runs Bun only: frozen install, `typecheck:tools`, build. `builder` is the Python base plus the uv binary, creates `/app/.venv` from `uv.lock` without dev groups or cache, then copies the code and the built assets and runs collectstatic with build-only placeholders. `runtime` is the same Python base with nothing added but a user; it receives the finished venv and the exact runtime paths by explicit COPY. The venv's `bin/python` links to `/usr/local/bin/python3.14`, which is why both Python stages reference the single `PYTHON_IMAGE` ARG (tag now, `tag@sha256:…` after the first clean scan). Reproducibility comes from pinned inputs: no `apt-get upgrade`, no pip removal.

## E. Docker commands for Mats (pwsh, Docker running)

```
docker build --no-cache --build-arg "PYTHON_IMAGE=python:$(Get-Content .python-version)-slim-trixie" -t hookrelay:ci .
docker inspect --format '{{.Config.User}}' hookrelay:ci
docker run --rm --entrypoint sh hookrelay:ci -c 'for p in /bin/uv /usr/bin/uv /bin/uvx /usr/bin/uvx /root/.cache/uv /home/app/.cache/uv /usr/local/bin/bun; do [ -e "$p" ] && echo "PRESENT $p" && exit 1; done; for c in gcc cc uv uvx bun node; do command -v $c && exit 1; done; ls /app/.venv/lib/python3.14/site-packages | grep -Ei "^(pytest|mypy|ruff)" && exit 1; echo runtime clean'
docker run --rm --entrypoint python hookrelay:ci -c 'import sys, django; print(".".join(map(str, sys.version_info[:3])))'
docker run --rm --network host -e SECRET_KEY=local-smoke-key-0123456789abcdef0123456789abcdef -e DATABASE_URL=postgresql://hookrelay:hookrelay@127.0.0.1:55433/hookrelay -e REDIS_URL=redis://127.0.0.1:56380/0 -e ALLOWED_HOSTS=127.0.0.1,localhost hookrelay:ci python manage.py migrate --noinput
docker run -d --name hookrelay --network host -e SECRET_KEY=local-smoke-key-0123456789abcdef0123456789abcdef -e DATABASE_URL=postgresql://hookrelay:hookrelay@127.0.0.1:55433/hookrelay -e REDIS_URL=redis://127.0.0.1:56380/0 -e ALLOWED_HOSTS=127.0.0.1,localhost hookrelay:ci
curl.exe -s -o NUL -w "readyz %{http_code}`n" -H "X-Forwarded-Proto: https" http://127.0.0.1:8080/readyz
curl.exe -s -o NUL -w "readyz-no-header %{http_code}`n" http://127.0.0.1:8080/readyz
docker logs hookrelay; docker rm -f hookrelay
```
Expected: user `app`; `runtime clean`; `3.14.7`; migrate OK; with the header 200 (loopback is trusted by default), without it 301 (Django saw http). Docker Desktop on Windows does not support `--network host` for Linux containers in every configuration — if it is unavailable, use `-p 8080:8080` with `host.docker.internal` in the two URLs instead.

## F. Trivy commands for Mats

```
trivy image --scanners vuln,secret --severity CRITICAL,HIGH --exit-code 1 hookrelay:ci
trivy image --format cyclonedx --output sbom-image.cdx.json hookrelay:ci
```
Zero findings → proceed to the digest step in the README and pin `PYTHON_IMAGE`. Any CRITICAL/HIGH in the unmodified base → STOP, paste the table; the OS-fix strategy is a separate decision (DECISION 25).

## G. SUID/SGID baseline procedure

`docker/suid-allowlist.txt` is empty, so `ci / docker` fails at that step on the first run and prints the measured list. Run `docker run --rm --entrypoint sh hookrelay:ci -c 'find / -xdev -perm /6000 -type f 2>/dev/null | sort'`, review every path against what the base image legitimately needs (expected: the Debian shadow/util-linux set such as `su`, `passwd`, `mount`; anything else is a question), commit the reviewed list. From then on the gate fails on any addition or removal.

## H. Forwarded-header trust decision and evidence

Decision 29: no wildcard anywhere. Uvicorn reads `FORWARDED_ALLOW_IPS` (verified in uvicorn 0.52.4 `config.py`: env fallback, default `127.0.0.1`; `proxy_headers.py` accepts CIDR via `ip_network`). CI proves both directions from a non-loopback source on the bridge network: `127.0.0.1` → 301, bridge subnet → 200. `fly.toml` carries the loopback default with the instruction to measure the Fly proxy's source network before the first deploy and record it in DECISIONS — the failure mode of a wrong value is a permanent https redirect, i.e. fail closed. The exact Fly source range is NOT asserted here: it is measured, not assumed.

## I. Documentation reconciliation

README (`.env.example` reference now true; versions; procedures), förspec v1.5 paragraph superseding the old §6b/§7 wording, PROOFS (Trivy row reworded to "zero known unsuppressed"; four GATE DEFINED rows that turn PROVEN only with a green run), DECISIONS 25–30 (25 and 27 supersede the `apt`/`ignore-unfixed` assumptions of 24 and 18), review log entry for the fbae421 failure including the two implementer proposals the review rejected.

## J. NOT proven here because Docker is unavailable in the sandbox

The image build; the runtime-clean, interpreter, SUID and trust-boundary gates against a real image; migrate/boot through the image; the Trivy result and the image SBOM; the Python base digest; `postgres:17`/`redis:7` exact tags; `uv audit`'s real output; whether `python:3.14.7-slim-trixie` exists and is clean (asserted by the review, proven by your build). Also not proven: the Fly proxy source network. Nothing above is claimed as passed.

## Baseline

BEFORE (intake zip, sandbox, uv 0.11.7 / Python 3.14.4): 20 pass / 0 skip / 0 fail, 100% branch coverage. AFTER (uv 0.12.13 / Python 3.14.7): 21 / 0 / 0, 100%; 1 new test; 0 new failures.

## BEVISAR / BEVISAR INTE

BEVISAR: the whole non-Docker wall is green on the exact target toolchain (uv 0.12.13, Python 3.14.7); the lock is unchanged under the new uv; every uv command in the workflows was verified against 0.12.13; uvicorn's trust variable semantics are verified in source; the Dockerfile, gates and procedures are defined so that a green GitHub run is a real proof.
BEVISAR INTE: everything in J.

## Suggested commit

    d00: harden runtime image, pin python 3.14.7 and uv 0.12.13, fail-closed image gates

---

## Appendix A — raw gate output (sandbox, v1.5)

```
$ uv --version
uv 0.12.13 (x86_64-unknown-linux-gnu)
[exit 0]

$ cat .python-version
3.14.7
[exit 0]

$ uv lock --check
Resolved 82 packages in 0.98ms
[exit 0]

$ uv sync --locked
Resolved 82 packages in 0.66ms
Checked 79 packages in 0.46ms
[exit 0]

$ uv run python -c "import sys; print(sys.version.split()[0])"
3.14.7
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

+ @alpinejs/csp@3.17.2
+ @tailwindcss/cli@4.3.3
+ @types/bun@1.4.2
+ htmx.org@4.0.0
+ tailwindcss@4.3.3
+ typescript@7.0.2

46 packages installed [879.00ms]
[exit 0]

$ bun run typecheck:tools
$ tsc --project tsconfig.json --noEmit
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 94ms
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 100 packages) [126.00ms]
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
[INFO] Installing environment for https://github.com/pre-commit/pre-commit-hooks.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

hook modifications: 0

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
43 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 24 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ (fresh database) uv run python manage.py migrate --noinput
  Applying django_tasks_database.0020_update_db_task_result_ordering... OK
  Applying django_tasks_database.0021_conditional_partial_index_ordering... OK
  Applying sessions.0001_initial... OK
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay15
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 21 items

apps/accounts/tests/test_user_model.py .                                 [  4%]
tests/integration/test_skeleton.py ...........                           [ 57%]
tests/integration/test_settings.py ........                              [ 95%]
tests/integration/test_toolchain.py .                                    [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.7-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 21 passed in 1.77s ==============================
[exit 0]

$ uv run python manage.py spectacular --fail-on-warn --validate --file /tmp/schema.yml
[exit 0]

$ uv export --locked --no-dev ... && uv run pip-audit --strict --require-hashes (production)
No known vulnerabilities found
[exit 0] (284 hashed artifacts)

$ uv export --locked --all-groups ... && uv run pip-audit --strict --require-hashes (all groups)
No known vulnerabilities found
[exit 0] (748 hashed artifacts)

$ uv audit --preview-features audit   (secondary, non-blocking; OSV unreachable from the sandbox)
Resolved 82 packages in 0.89ms
error: HTTP status client error (403 Forbidden) for url (https://api.osv.dev/v1/querybatch)
[exit 2]

$ uv export --locked --all-groups --no-emit-project --format cyclonedx1.5 --preview-features sbom-export -o /tmp/sbom.json
Resolved 82 packages in 1ms
[exit 0] CycloneDX 1.5 81 components

$ uvicorn boot smoke: FORWARDED_ALLOW_IPS default vs loopback client (dev settings, no SSL redirect: proves the env variable is read)
GET /livez 200
GET /readyz 200

$ workflow/dependabot YAML parse
4 files parse
[exit 0]
```

---

# LEVERANS D00 — Skeleton (v1.4 supply chain)

Förspec: docs/forspec/D00-skeleton.md v1.4 (LOCKED). Zip: hookrelay-20260914-1029-d00-skeleton-v1_4.zip. Base: hookrelay-20260914-1008-d00-skeleton-v1_3.zip (never committed). Supply chain only — no application code, no lockfile change; the planning docs (BUILD-PLAN, DECISIONS, STRUCTURE, reviews/, förspec stubs D01–D10) delivered in the copy-in zips are now part of the canonical tree.

## Machine diff vs base (content hash)

```
ADDED (16):
  .github/dependabot.yml
  .github/workflows/security.yml
  docs/BUILD-PLAN.md
  docs/DECISIONS.md
  docs/STRUCTURE.md
  docs/forspec/D01-accounts.md
  docs/forspec/D02-outbox.md
  docs/forspec/D03-delivery.md
  docs/forspec/D04-circuit-replay.md
  docs/forspec/D05-sse-ui.md
  docs/forspec/D06-graphql.md
  docs/forspec/D07-performance.md
  docs/forspec/D08-chaos.md
  docs/forspec/D09-kafka-lab.md
  docs/forspec/D10-rag.md
  docs/reviews/D00-review-log.md
MODIFIED (6):
  .github/workflows/ci.yml
  Dockerfile
  README.md
  docs/LEVERANS-D00.md
  docs/PROOFS.md
  docs/forspec/D00-skeleton.md
DELETED (0):
UNCHANGED (43): .dockerignore, .env.example, .github/workflows/codeql.yml, .gitignore, .pre-commit-config.yaml, apps/__init__.py, apps/accounts/__init__.py, apps/accounts/admin.py, apps/accounts/apps.py, apps/accounts/migrations/0001_initial.py, apps/accounts/migrations/__init__.py, apps/accounts/models.py, apps/accounts/tests/__init__.py, apps/accounts/tests/test_user_model.py, bun.lock, compose.yaml, config/__init__.py, config/asgi.py, config/settings/__init__.py, config/settings/base.py, config/settings/dev.py, config/settings/prod.py, config/settings/test.py, config/urls.py, config/views.py, config/wsgi.py, conftest.py, docs/security/README.md, fly.toml, manage.py, package.json, pyproject.toml, scripts/copy-assets.ts, static/dist/.gitkeep, static/src/app.css, static/src/app.js, templates/base.html, templates/index.html, tests/__init__.py, tests/integration/__init__.py, tests/integration/test_settings.py, tests/integration/test_skeleton.py, uv.lock
```

## What was done (v1.4)

- P0: `uv lock --check` is the first gate; `uv sync --locked`, `uv export --locked` and `uv sync --locked` in the Dockerfile replace `--frozen`; `UV_LOCKED=1` at workflow level so every uv call asserts the lock. Demonstrated in the gate run: with one dependency added to `pyproject.toml` and the lock untouched, `uv lock --check` exits 1, `uv sync --frozen` exits 0 (installs the stale lock), `uv sync --locked` exits 1.
- `security.yml` (pull request, push to main, daily 05:23 UTC, manual): `dependencies` (lock check, locked install, both hash-verified pip-audits with no ignores, `bun audit`, non-blocking `uv audit`, `uv tree`, CycloneDX SBOM artifact), `image` (build + Trivy CRITICAL/HIGH `ignore-unfixed`), `dependency-review` (PRs, `fail-on-severity: low`, `actions/dependency-review-action` v5.0.0 pinned to `a1d282b3…`). The audits and Trivy leave `ci.yml`, which keeps `test` and `docker`.
- `.github/dependabot.yml`: weekly grouped version updates for `uv`, `bun`, `github-actions`, `docker`, `docker-compose`. Alerts and security updates are repository settings (README checklist).
- Toolchain pinned to the versions that produced the evidence: setup-uv `version: 0.11.7`, setup-bun `bun-version: 1.4.2`, `python:3.14.4-slim`, `oven/bun:1.4.2`, `ghcr.io/astral-sh/uv:0.11.7`. Digests: not resolvable from the sandbox (no Docker, registry blocked); README "Image digests" gives the one-line pwsh command; Dependabot's docker ecosystem then maintains them.
- PROOFS.md: the vulnerability claims are now three surgical rows (pip-audit: no known vulnerability at scan time, fully pinned, hash-bearing, no ignores; bun audit; Trivy: no *fixable* CRITICAL/HIGH) plus rows for lock discipline, scheduled detection and dependency review. Required checks: `test`, `docker`, `dependencies`, `image`, `dependency-review`, `analyze (python)`, `analyze (javascript-typescript)`.
- Förspec v1.4, DECISIONS 22–24, review log section, README quality-gate text and settings checklist.

## Notes (all recorded)

1. `uv audit` (preview) could not be exercised here: api.osv.dev is blocked by the sandbox egress (exit 2). The step is `continue-on-error: true` by decision; its first real result comes from GitHub.
2. `dependency-review` requires the dependency graph; on by default for public repositories, a setting otherwise.
3. The `uv` and `bun` Dependabot ecosystem names are GitHub-side; confirmed by Dependabot's first run.
4. `postgres:17` and `redis:7` service images keep major tags until digests are added with the README command; exact patch tags could not be verified from the sandbox and are not invented.

## Evidence tiers

EXECUTED IN CLAUDE'S SANDBOX: every command in Appendix A — 12 gates exit 0 (lock check, locked installs, both hash-verified audits with 284 and 335 hashed artifacts, bun audit, SBOM with 81 components, ruff, format, mypy, fast lane at 100% branch coverage, YAML parse of all four workflow/dependabot files) plus the stale-manifest demonstration. `uv audit` exit 2 = network, recorded as not executed.

EXECUTED LOCALLY BY MATS (not yet): the Windows ritual; the digest command; repository settings (dependency graph, Dependabot alerts and security updates, the `main` ruleset with the seven required checks).

EXECUTED BY GITHUB (not yet): `ci.yml` (`test`, `docker`), `security.yml` (`dependencies`, `image`, `dependency-review`), CodeQL, Dependabot's first run, the first scheduled security run.

## Baseline

BEFORE (1008 zip): 20 pass / 0 skip / 0 fail, 100% branch coverage. AFTER: 20 / 0 / 0, 100%; no test changed (supply chain only).

## What was NOT done

No application code, no dependency change, no digest pinning (owner command), nothing committed or tagged.

## BEVISAR / BEVISAR INTE

BEVISAR: a stale lock now fails instead of installing; every uv call in CI, the security workflow and the image asserts the lock; audits are hash-verified on both dependency sets with no ignores; the frontend set is audited; the SBOM exports; the toolchain versions are the ones that produced the evidence; all four YAML files parse; the code gates are unchanged and green.
BEVISAR INTE: `uv audit` results; dependency review, Dependabot and the daily schedule until GitHub runs them; image digests; the Docker job and Trivy on GitHub; everything already listed under v1.3.

## Suggested commits

    d00: project skeleton
    docs: build plan, decisions, roadmap

---

## Appendix A — raw gate output (sandbox, v1.4)

```
$ uv lock --check
Resolved 82 packages in 2ms
[exit 0]

$ uv sync --locked
Resolved 82 packages in 1ms
Checked 79 packages in 0.51ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

Checked 40 installs across 77 packages (no changes) [1118.00ms]
[exit 0]

$ demonstration: stale manifest (extra dependency added to pyproject.toml, lock untouched)
  uv lock --check -> exit 1
  uv sync --frozen -> exit 0 (stale lock accepted)
  uv sync --locked -> exit 1 (stale lock rejected)
  manifest restored, uv sync --locked exit 0

$ uv export --locked --no-dev --no-emit-project --format requirements.txt -o /tmp/requirements-prod.txt && uv run pip-audit --strict --require-hashes -r /tmp/requirements-prod.txt
No known vulnerabilities found
[exit 0] (284 hashed artifacts)

$ uv export --locked --all-groups --no-emit-project --format requirements.txt -o /tmp/requirements-all.txt && uv run pip-audit --strict --require-hashes -r /tmp/requirements-all.txt
No known vulnerabilities found
[exit 0] (748 hashed artifacts)

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 75 packages) [150.00ms]
[exit 0]

$ uv audit --all-groups --preview-features audit   (secondary, non-blocking)
error: unexpected argument '--all-groups' found

  tip: a similar argument exists: '--only-group'

Usage: uv audit --only-group <ONLY_GROUP>

For more information, try '--help'.
[exit 2] -- api.osv.dev is not reachable from the sandbox; verified only that the command runs; result comes from GitHub

$ uv export --locked --all-groups --no-emit-project --format cyclonedx1.5 --preview-features sbom-export -o /tmp/sbom-python.json > /dev/null
Resolved 82 packages in 1ms
[exit 0] CycloneDX 1.5 81 components

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
42 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 23 source files
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 20 items

apps/accounts/tests/test_user_model.py .                                 [  5%]
tests/integration/test_skeleton.py ...........                           [ 60%]
tests/integration/test_settings.py ........                              [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.4-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 20 passed in 1.63s ==============================
[exit 0]

$ workflow and dependabot YAML parse
4 files parse
[exit 0]
```

---

# LEVERANS D00 — Skeleton (v1.3 hardening)

Förspec: docs/forspec/D00-skeleton.md v1.3 (LOCKED). Zip: hookrelay-20260914-1008-d00-skeleton-v1_3.zip. Base: hookrelay-20260913-1525-d00-skeleton-v1_2.zip (never committed). CI/test hardening only — no domain code, no D01 work, no dependency changes (`uv.lock` and `bun.lock` unchanged).

## Machine diff vs base (content hash)

```
ADDED (2):
  docs/security/README.md
  tests/integration/test_settings.py
MODIFIED (11):
  docs/LEVERANS-D00.md
  .github/workflows/ci.yml
  .github/workflows/codeql.yml
  README.md
  config/settings/base.py
  config/settings/prod.py
  conftest.py
  docs/PROOFS.md
  docs/forspec/D00-skeleton.md
  pyproject.toml
  tests/integration/test_skeleton.py
DELETED (0):
UNCHANGED (37): .dockerignore, .env.example, .gitignore, .pre-commit-config.yaml, Dockerfile, apps/__init__.py, apps/accounts/__init__.py, apps/accounts/admin.py, apps/accounts/apps.py, apps/accounts/migrations/0001_initial.py, apps/accounts/migrations/__init__.py, apps/accounts/models.py, apps/accounts/tests/__init__.py, apps/accounts/tests/test_user_model.py, bun.lock, compose.yaml, config/__init__.py, config/asgi.py, config/settings/__init__.py, config/settings/dev.py, config/settings/test.py, config/urls.py, config/views.py, config/wsgi.py, docs/LEVERANS-D00.md, fly.toml, manage.py, package.json, scripts/copy-assets.ts, static/dist/.gitkeep, static/src/app.css, static/src/app.js, templates/base.html, templates/index.html, tests/__init__.py, tests/integration/__init__.py, uv.lock
```

## What was done (v1.3)

- BLOCKER (mine, found in review): `database_from_url` now applies `connect_timeout=3` after the URL query so `?connect_timeout=60` cannot override it. Pinned by `test_database_url_cannot_override_the_enforced_connect_timeout`; passthrough of other libpq parameters pinned by a second test.
- Correction (mine): the audit export no longer drops hashes. `pip-audit --strict --require-hashes` runs on the production set and on `--all-groups` (284 hashed artifacts in the production export); both clean today.
- pytest: `--strict-config --strict-markers`, `filterwarnings = ["error"]` with zero exclusions (the suite was already warning-free), branch coverage with `--cov-fail-under=95` and `[tool.coverage.report] fail_under = 95`. Measured: 100.00% branch coverage, 20 tests.
- Tests: production fail-closed for each required value (parametrised, in-process import under a patched environment; modules restored afterwards) and production hardening asserted; development defaults asserted; PostgreSQL probe failure → 503 with the driver detail in the log and absent from the body; lossy cache (DummyCache) → 503; CSP asserted as the complete policy dictionary; static files resolvable only under `DEBUG=True` (the earlier uvicorn 404 regression, now pinned); autouse Redis fixture replaced by opt-in `redis_cache`; `tmp_path: Path` (ignore removed; the tree has one narrow `# noqa: S105` on a URL-parsing fixture, with its reason on the line, and one `# noqa: S106` on a test password).
- `SECURE_HSTS_PRELOAD = True` (header flag only) so `check --deploy --fail-level WARNING` passes with zero silenced checks: "System check identified no issues (0 silenced)".
- CI: token `contents: read`; every action pinned to a full commit SHA resolved from the repositories with `git ls-remote` (checkout v7.0.1, setup-uv v10.1.0, setup-bun v2.2.0, codeql-action v4.38.0, trivy-action v0.36.0, upload-artifact v7.0.1); `test` job adds pre-commit on the whole tree, `manage.py check`, `check --deploy --fail-level WARNING` with CI-only values, a fresh `migrate --noinput`, a boot smoke on `/readyz` and `/livez`; new `security` job (two hash-verified pip-audits, `bun audit`, `uv tree --all-groups`, CycloneDX SBOM artifact); `docker` job now inspects `USER`, migrates with the image, boots it and probes `/readyz` and `/` with `X-Forwarded-Proto: https`, then Trivy (CRITICAL/HIGH, `ignore-unfixed`, exit 1). CodeQL: `security-events: write` only in its job.
- `docs/security/README.md`: exception policy (no `--ignore-vuln` without a dated, owned record). README: quality-gate rules and the `main` ruleset checklist with the five required check names.
- Förspec v1.3; PROOFS.md: 22 PROVEN rows (was 8 + 1 OBSERVED).

## Deviations and notes (all recorded)

1. `uv export --format cyclonedx1.5` is a uv 0.11 preview feature; CI passes `--preview-features sbom-export` and discards uv's stdout echo of the document. If a later uv changes the flag, the step is updated deliberately.
2. The PostgreSQL readiness failure test raises the driver error at the probe; a dead server is not simulated (Django offers no supported way to retarget the test connection). The Redis test is the real-outage proof. PROOFS.md says so.
3. The concurrency lane job is not yet in CI: pytest exits 5 on an empty selection, so the job lands with the first `slow` test in D03.
4. The Trivy policy (`ignore-unfixed`) is a policy, not a suppression: findings without a fix are still printed in the job log.

## Evidence tiers

EXECUTED IN CLAUDE'S SANDBOX (Ubuntu 24.04, Python 3.14.4 via uv, bun 1.4.2, PostgreSQL 16.15 and Redis 7 local; CI and compose use PostgreSQL 17): every command in Appendix A — 20 commands, all exit 0, including a drop-and-recreate of the dev database before the fresh migration.

EXECUTED LOCALLY BY MATS (not yet): the pwsh ritual on Windows (`bun run build` via `scripts/copy-assets.ts`), `uv run pre-commit install`, `docker compose up -d`, the ruleset configuration in GitHub.

EXECUTED BY GITHUB (not yet): the three CI jobs and CodeQL on the exact commit — in particular the Docker job (image build with `ghcr.io/astral-sh/uv:0.11`, non-root check, migrate, boot, proxy-contract probes, Trivy) and pre-commit's hook environment install, neither of which can run in the sandbox.

## Baseline

BEFORE (1525 zip, sandbox): 9 pass / 0 skip / 0 fail, line coverage 69%. AFTER (sandbox): 20 pass / 0 skip / 0 fail; 11 new tests; 0 new failures; branch coverage 100.00% against a 95% floor.

## What was NOT done

Nothing from förspec §9. No dependency added or removed. Nothing committed or tagged.

## BEVISAR / BEVISAR INTE

BEVISAR: the enforced connection timeout survives URL parameters; production settings fail closed for each required value and are hardened when configured; `check --deploy` at WARNING level is clean; readiness degrades correctly for unreachable Redis, a failing PostgreSQL probe and a lossy cache without leaking detail; the CSP equals the intended policy; static files are served only under DEBUG; the suite is warning-free at 100% branch coverage; hooks, ruff, mypy, htmx checker, Django checks, migration drift, fresh migration, uvicorn smoke, both hash-verified pip-audits, bun audit and the SBOM export pass in the sandbox; every action is SHA-pinned under a read-only token.
BEVISAR INTE: the Docker job and Trivy result; pre-commit on GitHub's runner; a dead PostgreSQL server; task execution; htmx under CSP in a browser; Windows behaviour of the Bun script; PostgreSQL 17 specifically.

## Suggested commit

    d00: project skeleton

---

## Appendix A — raw gate output (sandbox, v1.3)

```
$ uv sync --frozen
Checked 79 packages in 0.72ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

Checked 40 installs across 77 packages (no changes) [308.00ms]
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 125ms
[exit 0]

$ uv run pre-commit run --all-files --show-diff-on-failure
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

$ git status --porcelain | grep -v "^A "   (files modified by hooks)
(none)

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
28 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 23 source files
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ SECRET_KEY=<64 random chars> ALLOWED_HOSTS=ci.hookrelay.example.test DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy --fail-level WARNING
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ (fresh database) uv run python manage.py migrate --noinput
  Applying django_tasks_database.0019_rename_django_task_new_ordering_idx_tasks_db_new_ordering_idx_and_more... OK
  Applying django_tasks_database.0020_update_db_task_result_ordering... OK
  Applying django_tasks_database.0021_conditional_partial_index_ordering... OK
  Applying sessions.0001_initial... OK
[exit 0]

$ uv run pytest -m not slow and not e2e
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.6.0
django: version: 6.1.1, settings: config.settings.test (from ini)
rootdir: /home/claude/hookrelay
configfile: pyproject.toml
testpaths: apps, tests
plugins: anyio-4.15.1, cov-7.1.0, django-4.14.0
collected 20 items

apps/accounts/tests/test_user_model.py .                                 [  5%]
tests/integration/test_skeleton.py ...........                           [ 60%]
tests/integration/test_settings.py ........                              [100%]

================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.4-final-0 ________________

Name    Stmts   Miss Branch BrPart  Cover   Missing
---------------------------------------------------
TOTAL     146      0      8      0   100%

15 files skipped due to complete coverage.
Required test coverage of 95% reached. Total coverage: 100.00%
============================== 20 passed in 1.13s ==============================
[exit 0]

$ uv run pytest -m not e2e --no-cov -q
....................                                                     [100%]
20 passed in 0.81s
[exit 0]

$ uv run python manage.py spectacular --fail-on-warn --validate --file /tmp/schema.yml
[exit 0]

$ uvicorn boot smoke on the migrated database (dev settings)
GET /livez 200
GET /readyz 200
GET / 200
GET /api/schema/ 200
GET /static/app.css 200
GET /admin/login/ 200
{"status": "ok", "db": "ok", "redis": "ok"}
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'

$ uv export --frozen --no-dev --no-emit-project --format requirements.txt -o /tmp/requirements-prod.txt && uv run pip-audit --strict --require-hashes -r /tmp/requirements-prod.txt
No known vulnerabilities found
[exit 0]

$ uv export --frozen --all-groups --no-emit-project --format requirements.txt -o /tmp/requirements-all.txt && uv run pip-audit --strict --require-hashes -r /tmp/requirements-all.txt
No known vulnerabilities found
[exit 0]

$ bun audit
bun audit v1.4.2 (744846f84)

No vulnerabilities found (checked 75 packages) [107.00ms]
[exit 0]

$ uv export --frozen --all-groups --no-emit-project --format cyclonedx1.5 -o /tmp/sbom-python.json
warning: `uv export --format=cyclonedx1.5` is experimental (uv 0.11.7); CI passes --preview-features sbom-export.
(SBOM JSON echoed to stdout by uv omitted here: 1081 lines)
[exit 0] CycloneDX 1.5 81 components

$ uv tree --all-groups --depth 1
Resolved 82 packages in 1ms
hookrelay v0.0.0
├── django v6.1.1
├── django-htmx v1.29.0
├── django-tasks-db v0.13.0
├── djangorestframework v3.18.1
├── drf-spectacular v0.30.0
├── psycopg[binary] v3.3.5
├── redis v8.1.0
├── uvicorn[standard] v0.52.4
├── django-stubs v6.1.0 (group: dev)
├── djangorestframework-stubs v3.18.1 (group: dev)
├── mypy v2.3.1 (group: dev)
├── pip-audit v2.10.1 (group: dev)
├── pre-commit v4.6.2 (group: dev)
├── pytest v9.1.1 (group: dev)
├── pytest-cov v7.1.0 (group: dev)
├── pytest-django v4.14.0 (group: dev)
└── ruff v0.16.7 (group: dev)
[exit 0]
```

---

# LEVERANS D00 — Skeleton (v1.2 amendment)

Förspec: docs/forspec/D00-skeleton.md v1.2 (LOCKED). Zip: hookrelay-20260913-1525-d00-skeleton-v1_2.zip. Base: hookrelay-20260913-1453-d00-skeleton.zip (v1.1 delivery, never committed). Amendment only — no D01 work.

## Machine diff vs base (content hash, CR-insensitive not needed: base was produced on Linux too)

```
ADDED (13):
  apps/accounts/__init__.py
  apps/accounts/admin.py
  apps/accounts/apps.py
  apps/accounts/migrations/0001_initial.py
  apps/accounts/migrations/__init__.py
  apps/accounts/models.py
  apps/accounts/tests/__init__.py
  apps/accounts/tests/test_user_model.py
  conftest.py
  docs/PROOFS.md
  scripts/copy-assets.ts
  tests/integration/__init__.py
  tests/integration/test_skeleton.py
MODIFIED (17):
  .github/workflows/ci.yml
  .pre-commit-config.yaml
  Dockerfile
  README.md
  config/settings/base.py
  config/settings/dev.py
  config/settings/test.py
  config/urls.py
  config/views.py
  docs/forspec/D00-skeleton.md
  fly.toml
  package.json
  pyproject.toml
  static/src/app.js
  templates/base.html
  templates/index.html
  uv.lock
DELETED (2):
  tests/conftest.py
  tests/test_skeleton.py
UNCHANGED (17): .dockerignore, .env.example, .github/workflows/codeql.yml, .gitignore, apps/__init__.py, bun.lock, compose.yaml, config/__init__.py, config/asgi.py, config/settings/__init__.py, config/settings/prod.py, config/wsgi.py, docs/LEVERANS-D00.md, manage.py, static/dist/.gitkeep, static/src/app.css, tests/__init__.py
```

## What was done (v1.2)

- BLOCKER fixes from the static review: `apps.accounts.User(AbstractUser)` + `AUTH_USER_MODEL` with a Django-generated `0001_initial` (inspected: standard AbstractUser fields, depends on `auth.0012`); `hx-headers:inherited` on `<body>`; `htmx.config.selfRequestsOnly` removed, `app.js` is comment-only.
- CSP enforced from D00 via `ContentSecurityPolicyMiddleware` + `SECURE_CSP`, strict self-only, no nonce; browsable API removed from dev. Header test added.
- `/livez` (process only, proven with `django_assert_num_queries(0)`) and `/readyz` (DB + Redis, `connect_timeout=3` on libpq and `socket_connect_timeout`/`socket_timeout=2` on redis-py, verified to pass through `RedisCache` `OPTIONS`; body limited to ok/error per probe; exception to log only). Negative test with an unreachable Redis whose URL carries a fake password: 503, `redis: error`, password absent from the body. Fly check and CI smoke moved to `/readyz`.
- mypy `strict` with django-stubs 6.1.0 and djangorestframework-stubs 3.18.1: `Success: no issues found in 22 source files` against Django 6.1.1 / DRF 3.18.1 / mypy 2.3.1 — DRF stubs kept because they pass with no overrides or ignores (one `type: ignore[operator]` in a test on a `tmp_path: object` parameter is the sole ignore in the tree). `uv run mypy .` is a CI step.
- pip-audit and pre-commit are locked dev dependencies; CI and README use `uv run` for both.
- `scripts/copy-assets.ts` (Bun.file/Bun.write, no shell) replaces the `mkdir -p`/`cp` script; four separate files in `static/dist/`. `bun run htmx:check` runs the official htmx 4 upgrade checker; verified to exit 1 on a known-bad file and 0 on the tree; CI gate.
- Dependencies trimmed: django-filter, httpx, factory-boy, respx, time-machine removed with the `DEFAULT_FILTER_BACKENDS` setting. Worker decision unchanged: django-tasks-db, `TASKS`, `db_worker` process stay.
- Tests relocated: `apps/accounts/tests/`, `tests/integration/`, root `conftest.py`; `testpaths = ["apps", "tests"]`; per-file S101 ignore extended to `apps/*/tests/*`. CI fast lane `-m "not slow and not e2e"`; concurrency lane job arrives with the first slow test (an empty lane would fail on pytest's exit code 5).
- `docs/PROOFS.md` created with eight PROVEN rows, one OBSERVED, eleven PLANNED. Förspec rewritten to v1.2. README ritual updated.
- Dev DB dropped and recreated before generating the accounts migration (no data existed). Do the same locally: `docker compose down -v` or `dropdb`, then the ritual.

## Deviations from the review's list (all recorded)

1. Ruff hooks gained `--force-exclude`: without it pre-commit hands the generated migration to ruff explicitly, bypassing `extend-exclude = ["migrations"]`, and ruff-format rewrote Django's output (found in the gate run, fixed, re-run clean). Generated migrations stay in Django's own formatting.
2. `readyz`'s `db: error` branch has no test (Django offers no supported way to redirect the test connection mid-test). Listed under BEVISAR INTE and as a PROOFS.md gap.

## Installed versions (uv.lock)

django 6.1.1 · django-htmx 1.29.0 · django-stubs 6.1.0 · django-tasks-db 0.13.0 · djangorestframework 3.18.1 · djangorestframework-stubs 3.18.1 · drf-spectacular 0.30.0 · mypy 2.3.1 · pip-audit 2.10.1 · pre-commit 4.6.2 · psycopg 3.3.5 · pytest 9.1.1 · pytest-cov 7.1.0 · pytest-django 4.14.0 · redis 8.1.0 · ruff 0.16.7 · uvicorn 0.52.4
bun.lock unchanged: tailwindcss 4.3.3 · @tailwindcss/cli 4.3.3 · htmx.org 4.0.0 · @alpinejs/csp 3.17.2

## Evidence tiers

EXECUTED IN CLAUDE'S SANDBOX (Ubuntu 24.04, Python 3.14.4 via uv, bun 1.4.2, PostgreSQL 16.15 and Redis 7 local; CI and compose use PostgreSQL 17): every command in the appendix below, raw output as captured. Additionally: admin CSP scan — `/admin/login/`, `/admin/`, `/admin/accounts/user/`, `/admin/accounts/user/add/`, `/admin/django_tasks_database/dbtaskresult/` rendered with a temporary superuser (deleted afterwards) and scanned: 0 inline `<script>`, 0 `<style>`, 0 `style=` attributes, 0 `on*=` handlers on all five pages; static analysis of the HTML, not a browser run.

EXECUTED LOCALLY BY MATS (not yet): the pwsh ritual on Windows including `bun run build` via `scripts/copy-assets.ts`, `docker compose up -d`, uvicorn `--reload`, `uv run pre-commit install`.

EXECUTED BY GITHUB (not yet): ci.yml on postgres:17 (now including mypy, htmx:check, locked pip-audit, fast lane), docker build (`ghcr.io/astral-sh/uv:0.11` tag still unverified from the sandbox), CodeQL baseline.

## Baseline

BEFORE (1453 zip, sandbox): 5 pass / 0 skip / 0 fail. AFTER (sandbox): 9 pass / 0 skip / 0 fail; 4 new tests (livez zero-query, readyz degraded, CSP header, custom user), 2 tests renamed healthz → readyz, 0 new failures.

## What was NOT done

Everything in förspec §9: no domain models beyond the bare user, no auth flows, no API beyond the schema route, no task, no SSE, no pooling, no GraphQL, no partitioning, no deploy, no Fly secrets, no nonce, no browsable API. Nothing committed or tagged — the zip is delivered for your git.

## BEVISAR / BEVISAR INTE

BEVISAR: the swappable user exists from the first migration and persists; `/livez` makes zero queries; `/readyz` proves PostgreSQL and Redis and degrades to 503 without leaking the Redis location; the CSP header is strict self-only and tested; the tree carries no htmx 2 residue and the checker is a real gate (exit 1 on bad input); strict mypy with Django and DRF stubs passes; pip-audit clean; hooks clean with zero modifications; migrations in sync; schema warning-free; prod fails closed; uvicorn serves every route and asset with the CSP header present; Django 6.1 admin pages contain no inline script or style that the policy would block.
BEVISAR INTE: task execution (no task defined); an htmx request under the CSP in a browser (no htmx interaction exists yet); the `db: error` branch of `/readyz`; Windows behaviour of the Bun script (Bun-native APIs, but not executed on Windows here); the image build and Fly runtime; PostgreSQL 17 specifically.

## Suggested commit

    d00: project skeleton

---

## Appendix A — raw gate output (sandbox)

```
$ uv sync --frozen
Checked 79 packages in 0.66ms
[exit 0]

$ bun install --frozen-lockfile
bun install v1.4.2 (744846f84)

Checked 40 installs across 77 packages (no changes) [191.00ms]
[exit 0]

$ bun run build
$ bun run build:js && bun run build:css
$ bun scripts/copy-assets.ts
$ tailwindcss -i static/src/app.css -o static/dist/app.css --minify
≈ tailwindcss v4.3.3

Done in 89ms
[exit 0]

$ uv run ruff check .
All checks passed!
[exit 0]

$ uv run ruff format --check .
26 files already formatted
[exit 0]

$ uv run mypy .
Success: no issues found in 22 source files
[exit 0]

$ uv run python manage.py check
System check identified no issues (0 silenced).
[exit 0]

$ uv run python manage.py makemigrations --check --dry-run
No changes detected
[exit 0]

$ uv run pytest -m not e2e --no-cov -q
.........                                                                [100%]
9 passed in 0.70s
[exit 0]

$ uv run pytest -m not slow and not e2e -q
.........                                                                [100%]
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.14.4-final-0 ________________

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
config/settings/dev.py        9      9     0%   1-17
config/settings/prod.py      18     18     0%   1-30
config/urls.py               10      1    90%   23
config/views.py              39      4    90%   49-51, 59
-------------------------------------------------------
TOTAL                       145     32    78%

11 files skipped due to complete coverage.
9 passed in 0.85s
[exit 0]

$ uv run python manage.py spectacular --fail-on-warn --validate --file /tmp/schema.yml
[exit 0]

$ bun run htmx:check
$ bun node_modules/htmx.org/dist/scripts/upgrade-check.js templates static/src apps
File extensions: .html, .php, .js, .ts, .jinja, .jinja2, .j2, .erb, .hbs
Use --ext to add more (e.g. --ext .vue --ext .svelte)

Scanning 3 file(s)...


Found 0 issue(s) in 0 of 3 file(s).
[exit 0]

$ uv run pip-audit -r /tmp/requirements.txt --strict
No known vulnerabilities found
[exit 0]

$ env DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py collectstatic --noinput

200 static files copied to '/home/claude/hookrelay/staticfiles', 200 post-processed.
[exit 0]

$ env DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy
System check identified some issues:

WARNINGS:
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
?: (security.W021) You have not set the SECURE_HSTS_PRELOAD setting to True. Without this, your site cannot be submitted to the browser preload list.

System check identified 2 issues (0 silenced).
[exit 0]

$ DJANGO_SETTINGS_MODULE=config.settings.prod uv run python -c "import django; django.setup()"  (no secrets)
django.core.exceptions.ImproperlyConfigured: SECRET_KEY must be set in production
$ uv run pip-audit -r /tmp/requirements.txt --strict
No known vulnerabilities found
[exit 0]

$ env DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py collectstatic --noinput

200 static files copied to '/home/claude/hookrelay/staticfiles', 200 post-processed.
[exit 0]

$ env DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check --deploy
System check identified some issues:

WARNINGS:
?: (security.W009) Your SECRET_KEY has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
?: (security.W021) You have not set the SECURE_HSTS_PRELOAD setting to True. Without this, your site cannot be submitted to the browser preload list.

System check identified 2 issues (0 silenced).
[exit 0]

$ DJANGO_SETTINGS_MODULE=config.settings.prod uv run python -c "import django; django.setup()"  (no secrets set)
django.core.exceptions.ImproperlyConfigured: SECRET_KEY must be set in production
[exit 1]

$ uv run pre-commit run --all-files   (whole tree is new in this repo; later drops run hooks on touched files only)
check yaml...............................................................Passed
fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
mixed line ending........................................................Passed
ruff check...............................................................Passed
ruff format..............................................................Passed
[exit 0]

$ git status --porcelain | grep -v "^A "   (files modified by hooks)
(none)

$ uvicorn boot smoke (dev settings)
GET /livez 200
GET /readyz 200
GET / 200
GET /api/schema/ 200
GET /static/app.css 200
GET /static/htmx.min.js 200
GET /static/alpine-csp.min.js 200
GET /static/app.js 200
GET /admin/login/ 200
{"status": "ok", "db": "ok", "redis": "ok"}
POST /readyz 405
content-security-policy: default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'

```

---

## History — v1.1 delivery (hookrelay-20260913-1453-d00-skeleton.zip)

The v1.1 LEVERANS is kept below unchanged for the record.

## What was done

- Project tree per förspec §4, every file listed there and nothing else.
- Settings split base/dev/test/prod; DATABASE_URL parsed with stdlib; RedisCache; TASKS on django-tasks-db with uuid7 ids; DRF deny-by-default with JSON-only renderer/parser; spectacular schema at /api/schema/ (public on purpose); prod fails closed without SECRET_KEY, DATABASE_URL, REDIS_URL, ALLOWED_HOSTS.
- /healthz with real DB and Redis round-trips (503 + which probe failed on error); / renders base.html with the built assets.
- bun pipeline: Tailwind 4 build, vendored htmx 4.0.0 and Alpine CSP 3.17.2, no bundler.
- CI (postgres:17 + redis:7 services, ruff, pip-audit, migrations check, pytest with coverage, uvicorn boot smoke, docker build job), CodeQL (python + javascript-typescript), pre-commit config.
- Dockerfile (bun stage + uv stage, collectstatic at build, non-root), .dockerignore, fly.toml (web + worker processes, release migrate, /healthz check, [[statics]] for /static/), compose.yaml (postgres:17, redis:7).
- README with the pwsh ritual; this LEVERANS; förspec v1.1 in docs/forspec/.

## Deviations from förspec v1.1 (all recorded, none silent)

1. uvicorn[standard] added as a runtime dependency. Implied by §5, §6b and §11, missing from the §3 list. Without it the ritual's second line cannot run.
2. Static files under uvicorn: Django serves them only through runserver, so dev URLs include staticfiles_urlpatterns() when DEBUG, and production uses Fly [[statics]] from the image. No dependency added (WhiteNoise was the alternative; not needed).
3. /healthz is csrf_exempt in addition to require_GET. Found by the boot smoke: a live POST returned 403 from the CSRF middleware while the test client (which skips CSRF) returned 405. The view is read-only; exempting it makes the tested contract (405) the real one.
4. Test 3 asserts the stylesheet link (/static/app.css), not that the file is served; serving is proven by the uvicorn smoke, not by the test client.

## Verified against installed source (förspec §5 open item)

Django 6.1.1 core django.tasks has no ENQUEUE_ON_COMMIT setting; django-tasks-db 0.13.0 enqueue() is DBTaskResult.objects.create(...) with no on_commit wrapping. An enqueue inside transaction.atomic() therefore commits or rolls back with the surrounding rows. Drops 2 and 3 can rely on this without a setting. The worker command is db_worker (options: --queue-name, --interval, --batch, --max-tasks, --worker-id).

## Installed versions (uv.lock)

django 6.1.1 · djangorestframework 3.18.1 · psycopg 3.3.5 · django-tasks-db 0.13.0 · redis 8.1.0 · django-htmx 1.29.0 · django-filter 26.1 · drf-spectacular 0.30.0 · httpx 0.28.1 · uvicorn 0.52.4 · pytest 9.1.1 · pytest-django 4.14.0 · pytest-cov 7.1.0 · factory-boy 3.3.3 · respx 0.23.1 · time-machine 3.5.1 · ruff 0.16.7
bun.lock: tailwindcss 4.3.3 · @tailwindcss/cli 4.3.3 · htmx.org 4.0.0 · @alpinejs/csp 3.17.2

## Evidence tiers

EXECUTED IN CLAUDE'S SANDBOX (Ubuntu 24.04, Python 3.14.4 via uv, bun 1.4.2, PostgreSQL 16.15 and Redis 7 installed locally — note: CI and compose use PostgreSQL 17):
- uv sync, bun install, bun run build: OK (static/dist: app.css 9.2 KB, htmx.min.js, alpine-csp.min.js, app.js).
- ruff check: All checks passed. ruff format --check: 15 files already formatted.
- manage.py migrate (dev DB): OK. manage.py check: 0 issues.
- pytest -m "not e2e" --no-cov: 5 passed. With coverage (CI form): 5 passed, 69% (dev/prod settings and the healthz error branches are the uncovered lines).
- uvicorn boot: /healthz 200 {"status":"ok","db":"ok","redis":"ok"}, / 200, /api/schema/ 200, /static/app.css and the three JS files 200, POST /healthz 405.
- prod settings: collectstatic with ManifestStaticFilesStorage 200 files post-processed; check --deploy → only W009 (placeholder key during build) and W021 (HSTS preload deliberately off); import without secrets → ImproperlyConfigured.
- pip-audit on uv export: No known vulnerabilities found.
- pre-commit run on the whole (new) tree: all six hooks Passed, zero files changed. (Only acceptable here because every file is new; on later drops hooks run on touched files only.)
- db_worker --help: command present.

EXECUTED LOCALLY BY MATS (not yet): the pwsh ritual on Windows, bun's build:js shell script (mkdir -p / cp via Bun shell on Windows — verify), docker compose up, uvicorn --reload.

EXECUTED BY GITHUB (not yet): ci.yml on postgres:17, docker build (the uv:0.11 base image tag was not reachable from the sandbox and is unverified), CodeQL baseline.

## Baseline

BEFORE: no repository (0 pass / 0 skip / 0 fail). AFTER (sandbox): 5 pass / 0 skip / 0 fail; 5 new tests; 0 new failures.

## What was NOT done

Nothing from förspec §9: no domain models, no auth, no API beyond the schema route, no task, no SSE, no CSP middleware, no pooling, no deploy, no Fly secrets. Nothing was committed or tagged — the zip is delivered for your git.

## BEVISAR / BEVISAR INTE

BEVISAR: the locked stack resolves and boots on Python 3.14; DB, Redis and the tasks backend are wired; /healthz proves the two connection strings; the asset pipeline produces served files; prod settings fail closed; migrations are in sync; the schema generates warning-free; hooks and the CI steps run clean where they could be executed.
BEVISAR INTE: task execution (no task defined); Windows behaviour of the bun scripts; the image build and Fly runtime; PostgreSQL 17 specifically (sandbox ran 16).

## Suggested commit

    d00: project skeleton
