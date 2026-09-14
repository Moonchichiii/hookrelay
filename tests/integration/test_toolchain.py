"""Toolchain invariants: one approved Python version, owned by .python-version.

The runtime half (the built image executes 3.14.7 from /app/.venv) is proven
in CI's docker job; the image tags carry no version, so nothing is parsed
from them.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APPROVED_PYTHON = "3.14.7"


def test_python_version_file_is_the_approved_version() -> None:
    assert (ROOT / ".python-version").read_text().strip() == APPROVED_PYTHON


def test_running_interpreter_matches_python_version_file() -> None:
    pinned = (ROOT / ".python-version").read_text().strip()

    assert ".".join(map(str, sys.version_info[:3])) == pinned
