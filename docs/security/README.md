# Security exceptions

CI blocks any known vulnerability with an available fix (`pip-audit --strict --require-hashes` on the production set and on all groups, `bun audit`, Trivy on the image at CRITICAL/HIGH with unfixed findings excluded). No `--ignore-vuln`, no severity downgrade and no scan skip is added to CI without a record in this directory.

An exception is a file `exceptions/<ADVISORY-ID>.md` containing: the advisory; the affected dependency and why it is present; whether production is affected; why exploitation is impossible or reduced here; the temporary mitigation; the owner; an expiry date; the condition under which the exception is removed. The CI suppression references the file, and the file is deleted with the suppression when the fix lands.

Remediation is a reviewed dependency update (`uv lock --upgrade-package <name>`, inspect the diff, full suite, commit), never an automated change made by CI.
