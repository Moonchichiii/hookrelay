"""No unapproved credential-shaped connection URI may be committed.

GitHub secret scanning reads source text. Fixtures build DSNs at runtime;
this gate fails the suite if a literal scheme://user:password@host appears in
the tree unless it is one of the explicit, reviewed synthetic combinations
below in one of the contexts that legitimately carry them. A loopback host is
not an exemption on its own: an unapproved credential on 127.0.0.1 still fails.
"""

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CREDENTIAL_URI = re.compile(
    r"\b(?P<scheme>postgres(?:ql)?|redis|rediss|amqp|amqps|mysql|mongodb|mongodb\+srv)://"
    r"(?P<user>[^\s/:@'\"`]*):(?P<password>[^\s@'\"`]+)@(?P<host>[^\s/:'\"`?]+)"
)

# (user, password, host): the compose development credentials on the local
# service hosts, and the Docker build-only placeholder. Nothing else.
APPROVED_FIXTURES = {
    ("hookrelay", "hookrelay", "127.0.0.1"),
    ("hookrelay", "hookrelay", "localhost"),
    ("hookrelay", "hookrelay", "host.docker.internal"),
    ("build", "build", "localhost"),
}
# Where those fixtures may appear: development defaults, CI services, the
# documented placeholder file, the build-only placeholder, the README's local
# commands, and the evidence logs under docs/.
APPROVED_CONTEXTS = (
    "config/settings/dev.py",
    "config/settings/test.py",
    ".env.example",
    ".github/workflows/ci.yml",
    "Dockerfile",
    "README.md",
    "docs/",
)


def find_unapproved_uris(text: str, relative_path: str) -> list[str]:
    hits = []
    for m in CREDENTIAL_URI.finditer(text):
        combination = (m.group("user"), m.group("password"), m.group("host"))
        in_context = relative_path.startswith(APPROVED_CONTEXTS)
        if combination in APPROVED_FIXTURES and in_context:
            continue
        hits.append(m.group(0))
    return hits


def tracked_text_files() -> list[Path]:
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git executable not found")

    result = subprocess.run(  # noqa: S603 - resolved Git executable; arguments are fixed
        [git, "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )

    return [
        ROOT / relative
        for relative in result.stdout.split("\0")
        if relative and (ROOT / relative).is_file()
    ]


def test_no_unapproved_credential_bearing_uri_is_committed() -> None:
    offenders = {}
    for path in tracked_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT).as_posix()
        hits = find_unapproved_uris(text, relative)
        if hits:
            offenders[relative] = hits

    assert offenders == {}


def test_detector_rejects_unapproved_secrets_even_on_loopback() -> None:
    # All samples are assembled at runtime; none exists as source text.
    at = chr(64)
    remote = f"postgresql://svc:{'fixture-' + 'pw'}{at}db.example.test:5432/app"
    loopback_secret = f"postgresql://admin:{'REAL_' + 'SECRET'}{at}127.0.0.1/hookrelay"
    approved = f"postgresql://hookrelay:hookrelay{at}127.0.0.1:55433/hookrelay"

    assert len(find_unapproved_uris(remote, "config/settings/dev.py")) == 1
    assert len(find_unapproved_uris(loopback_secret, "config/settings/dev.py")) == 1
    assert find_unapproved_uris(approved, "config/settings/dev.py") == []
    # An approved combination outside an approved context is still rejected.
    assert len(find_unapproved_uris(approved, "apps/accounts/models.py")) == 1
