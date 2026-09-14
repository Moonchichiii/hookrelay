"""Every external image reference the repository owns is pinned by digest.

Syntax and presence are enforced; the values themselves are the owner's
measured digests recorded in the D00 evidence and updated only deliberately.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIGEST_REF = re.compile(r"^[a-z0-9./_-]+(:[A-Za-z0-9._-]+)?@sha256:[0-9a-f]{64}$")
DOCKERFILE_ARGS = ("PYTHON_BUILDER_IMAGE", "PYTHON_RUNTIME_IMAGE", "UV_IMAGE", "BUN_IMAGE")


def dockerfile_args() -> dict[str, str]:
    args = {}
    for line in (ROOT / "Dockerfile").read_text().splitlines():
        if line.startswith("ARG ") and "=" in line:
            name, value = line[4:].split("=", 1)
            args[name.strip()] = value.strip()
    return args


def service_images(path: Path) -> list[str]:
    return [
        line.split("image:", 1)[1].strip()
        for line in path.read_text().splitlines()
        if line.strip().startswith("image:")
    ]


def test_dockerfile_base_images_are_digest_pinned() -> None:
    args = dockerfile_args()

    assert set(DOCKERFILE_ARGS) <= set(args)
    for name in DOCKERFILE_ARGS:
        assert DIGEST_REF.match(args[name]), f"{name}={args[name]}"


def test_compose_services_are_digest_pinned() -> None:
    images = service_images(ROOT / "compose.yaml")

    assert len(images) == 2
    assert all(DIGEST_REF.match(image) for image in images), images


def test_ci_service_images_are_digest_pinned() -> None:
    images = service_images(ROOT / ".github" / "workflows" / "ci.yml")

    assert len(images) == 4
    assert all(DIGEST_REF.match(image) for image in images), images


def test_digest_pattern_rejects_tag_only_and_malformed_digests() -> None:
    assert DIGEST_REF.match("postgres:17") is None
    assert DIGEST_REF.match("postgres:17@sha256:" + "0" * 63) is None
    assert DIGEST_REF.match("postgres:17@sha256:" + "G" * 64) is None
    assert DIGEST_REF.match("cgr.dev/chainguard/python:latest@sha256:" + "a" * 64)
