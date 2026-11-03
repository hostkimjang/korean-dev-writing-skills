#!/usr/bin/env python3
"""Build a reproducible, allowlisted skill ZIP without installing anything.

Only the explicit PACKAGE_FILES in check.py enter the archive. Repository
documentation, evaluations, Git metadata, hidden files, and unlisted resources
cannot enter through a recursive directory copy. ZIP entries use a fixed order,
1980-01-01 timestamps, Unix permissions, and ZIP_STORED compression so identical
input bytes produce identical archive bytes without depending on zlib versions.
"""

from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile

from check import PACKAGE_FILES, SKILL_NAME, SKILL_RELATIVE_PATH, validate_repository


DEFAULT_VERSION = "0.5.0"
FIXED_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
VERSION = re.compile(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")


def version_argument(value: str) -> str:
    value = value.removeprefix("v")
    if not VERSION.fullmatch(value):
        raise argparse.ArgumentTypeError("use a version such as 0.4.0 or 0.4.0-rc.1")
    return value


def entry_info(name: str, *, directory: bool = False) -> zipfile.ZipInfo:
    entry = zipfile.ZipInfo(name, FIXED_TIMESTAMP)
    entry.create_system = 3
    entry.compress_type = zipfile.ZIP_STORED
    entry.external_attr = ((stat.S_IFDIR | 0o755) if directory else (stat.S_IFREG | 0o644)) << 16
    if directory:
        entry.external_attr |= 0x10
    return entry


def build_archive(root: Path, output_directory: Path, version: str) -> Path:
    root = root.resolve()
    report = validate_repository(root, skill_only=True)
    if report.errors:
        raise ValueError("skill validation failed:\n" + "\n".join(report.errors))
    skill = root / SKILL_RELATIVE_PATH
    payloads = {f"{SKILL_NAME}/{relative}": (skill / relative).read_bytes() for relative in PACKAGE_FILES}
    directories = {f"{SKILL_NAME}/"}
    for name in payloads:
        directories.update(f"{parent.as_posix()}/" for parent in Path(name).parents if str(parent) != ".")
    output_directory = output_directory.resolve()
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / f"{SKILL_NAME}-v{version}.zip"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".skill-package-", suffix=".zip", dir=output_directory, delete=False) as handle:
            temporary = Path(handle.name)
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_STORED, strict_timestamps=True) as archive:
            for name in sorted(directories | payloads.keys()):
                archive.writestr(entry_info(name, directory=name in directories), b"" if name in directories else payloads[name])
        temporary.chmod(0o644)
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--version", type=version_argument, default=DEFAULT_VERSION, help=f"release version (default: {DEFAULT_VERSION})")
    parser.add_argument("--output-dir", type=Path, help="output directory (default: <repo-root>/dist)")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1], help="repository root (default: this script's repository)")
    args = parser.parse_args()
    root = args.repo_root.resolve()
    try:
        output = build_archive(root, args.output_dir or root / "dist", args.version)
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    print(f"Created {output}")
    print(f"SHA256 {digest}")
    print(f"Included {len(PACKAGE_FILES)} allowlisted files under {SKILL_NAME}/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
