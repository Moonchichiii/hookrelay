"""Fail-closed inspection of the exported runtime rootfs (CI, host side).

The production image has no shell, so nothing can be asked from inside it.
`docker export` gives the merged filesystem as a tar; this script checks exact
paths and mode bits with the standard library only.
"""

import sys
import tarfile

FORBIDDEN_FILES = {
    "bin/sh",
    "bin/bash",
    "bin/ash",
    "bin/dash",
    "bin/busybox",
    "usr/bin/sh",
    "usr/bin/bash",
    "usr/bin/ash",
    "usr/bin/dash",
    "usr/bin/busybox",
    "bin/uv",
    "usr/bin/uv",
    "usr/local/bin/uv",
    "app/.venv/bin/uv",
    "bin/uvx",
    "usr/bin/uvx",
    "usr/local/bin/uvx",
    "app/.venv/bin/uvx",
    "usr/bin/pip",
    "usr/bin/pip3",
    "usr/local/bin/pip",
    "usr/local/bin/pip3",
    "app/.venv/bin/pip",
    "app/.venv/bin/pip3",
    "usr/local/bin/bun",
    "usr/local/bin/bunx",
    "usr/bin/bun",
    "usr/bin/node",
    "usr/local/bin/node",
    "usr/bin/npm",
    "usr/local/bin/npm",
    "usr/bin/npx",
    "usr/bin/gcc",
    "usr/bin/cc",
    "usr/bin/g++",
    "usr/bin/c++",
    "usr/bin/make",
    "usr/bin/cmake",
    "usr/bin/ld",
    "sbin/apk",
    "usr/sbin/apk",
    "usr/bin/apk",
    "usr/bin/apt",
    "usr/bin/apt-get",
    "usr/bin/dpkg",
    "usr/bin/yum",
    "usr/bin/dnf",
    "usr/bin/sudo",
    "usr/bin/su",
    "app/.env",
    "app/conftest.py",
    "app/pyproject.toml",
    "app/uv.lock",
}

# These roots must not exist at all, in any form.
FORBIDDEN_TREE_ROOTS = (
    "app/tests",
    "app/docs",
    "app/node_modules",
    "app/.git",
    "app/.venv/.cache",
    "root/.cache",
    "home/nonroot/.cache",
    "home/app/.cache",
    "app/.cache",
)

# These upstream package-cache skeleton directories may exist EMPTY.
# Any content below them, or a non-directory entry at the root, is forbidden.
EMPTY_CACHE_ROOTS = (
    "var/cache/apk",
    "var/cache/apt",
    "var/lib/apt/lists",
)

FORBIDDEN_SITE_PACKAGES = (
    "pytest",
    "_pytest",
    "mypy",
    "ruff",
    "pip_audit",
    "pre_commit",
    "django_stubs",
    "coverage",
)

REQUIRED_ENTRIES = (
    "app/.venv/bin/uvicorn",
    "app/.venv/bin/python",
    "app/manage.py",
    "app/staticfiles/staticfiles.json",
)


def is_in_forbidden_tree(name: str) -> bool:
    return any(name == root or name.startswith(root + "/") for root in FORBIDDEN_TREE_ROOTS)


def cache_root_violation(name: str, member: tarfile.TarInfo) -> bool:
    for root in EMPTY_CACHE_ROOTS:
        if name == root:
            return not member.isdir()
        if name.startswith(root + "/"):
            return True
    return False


def entry_kind(member: tarfile.TarInfo) -> str:
    if member.isdir():
        return "directory"
    if member.issym():
        return "symlink"
    if member.islnk():
        return "hardlink"
    if member.isfile():
        return "file"
    return "other"


def main(path: str) -> int:
    violations: list[str] = []
    present: set[str] = set()

    with tarfile.open(path) as tar:
        for member in tar:
            name = member.name.lstrip("./")
            present.add(name)
            kind = entry_kind(member)

            if name in FORBIDDEN_FILES:
                violations.append(f"forbidden path ({kind}): /{name}")

            if is_in_forbidden_tree(name):
                violations.append(f"forbidden tree ({kind}): /{name}")

            if cache_root_violation(name, member):
                violations.append(f"forbidden cache content ({kind}): /{name}")

            if member.isdir():
                continue

            if name.startswith("app/.venv/lib/") and "/site-packages/" in name:
                top = name.split("/site-packages/", 1)[1].split("/", 1)[0]
                if top.split("-", 1)[0] in FORBIDDEN_SITE_PACKAGES:
                    violations.append(f"development package in runtime venv ({kind}): /{name}")

            if (member.isfile() or member.islnk()) and member.mode & 0o6000:
                violations.append(f"setuid/setgid bit ({kind}): /{name} mode {member.mode:o}")

    for required in REQUIRED_ENTRIES:
        if required not in present:
            violations.append(f"missing required entry: /{required}")

    if violations:
        print("ROOTFS INSPECTION FAILED")
        for line in sorted(set(violations)):
            print("  " + line)
        return 1

    print(
        f"rootfs clean: {len(present)} entries; no shell, package installer, "
        "build tooling, cache payloads or dev packages; 0 setuid/setgid files"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
