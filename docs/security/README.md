# Security exceptions

CI blocks any known vulnerability: `pip-audit --strict --require-hashes` on the production set and on all dependency groups, `bun audit`, and Trivy on the final runtime image at CRITICAL/HIGH — fixed or unfixed, vuln and secret scanners, OS and library. There is no generic ignore file, no severity downgrade, no `ignore-unfixed`, no soft-fail, and no `--ignore-vuln` in CI without a record in this directory.

A genuine temporary exception is a reviewed, dated VEX/waiver file `exceptions/<ADVISORY-ID>.md` containing: the advisory; the affected component and why it is present; whether production is affected; why exploitation is impossible or reduced here (evidence, not opinion); the temporary mitigation; the owner; an expiry/review date; the condition under which the exception is removed. The CI suppression references the file, and both are deleted when the fix lands. Until such a record exists, a red scan stays red.

Remediation is a reviewed dependency or base-image update (`uv lock --upgrade-package <name>`, a new pinned image digest), inspected, run through the full wall, committed — never an automated change made by CI.
