#!/usr/bin/env python3
"""Install with the pinned skills CLI in temporary projects and check file bytes.

Requires Node.js >=22.20, npm/npx, Git, and access to the npm registry.
The default source is the checked-out repository, so CI tests the current change.
An optional --source accepts the same repository through its public GitHub URL.
This checks installation only; it does not launch Claude Code or Codex.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from check import PACKAGE_FILES, SKILL_NAME, SKILL_RELATIVE_PATH


CLI_PACKAGE = "skills@1.7.5"
AGENT_PATHS = {"claude-code": ".claude/skills", "codex": ".agents/skills"}


def verify_install(project: Path, source: Path) -> None:
    expected = set(PACKAGE_FILES)
    for agent, directory in AGENT_PATHS.items():
        installed = project / directory / SKILL_NAME
        if not installed.is_dir():
            raise RuntimeError(f"{agent}: skill directory was not installed")
        if not installed.resolve().is_relative_to(project.resolve()):
            raise RuntimeError(f"{agent}: installation points outside the temporary project")
        actual = {p.relative_to(installed).as_posix() for p in installed.rglob("*") if p.is_file()}
        if actual != expected:
            raise RuntimeError(f"{agent}: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
        for relative in PACKAGE_FILES:
            if (installed / relative).read_bytes() != (source / relative).read_bytes():
                raise RuntimeError(f"{agent}: installed file differs: {relative}")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(repo), help="CLI source; defaults to this checkout")
    args = parser.parse_args()
    npx = shutil.which("npx")
    if not npx:
        raise SystemExit("npx is required; install Node.js 22.20 or later with npm.")
    if not shutil.which("git"):
        raise SystemExit("Git is required by the skills CLI.")
    with tempfile.TemporaryDirectory(prefix="korean-dev-writing-install-") as temporary:
        base = Path(temporary)
        environment = os.environ.copy()
        environment.update({
            "CI": "1",
            "DISABLE_TELEMETRY": "1",
            "npm_config_cache": str(base / "npm-cache"),
            "npm_config_fetch_retries": "0",
            "npm_config_fetch_timeout": "30000",
            "SKILLS_CLONE_TIMEOUT_MS": "60000",
        })
        for mode in ("default", "copy"):
            project = base / mode
            project.mkdir()
            command = [
                npx, "--yes", CLI_PACKAGE, "add", args.source,
                "--skill", SKILL_NAME,
                "--agent", "claude-code", "--agent", "codex", "--yes",
            ]
            if mode == "copy":
                command.append("--copy")
            print(f"Installing with {CLI_PACKAGE}: {mode} mode", flush=True)
            subprocess.run(command, cwd=project, env=environment, check=True, timeout=120)
            verify_install(project, repo / SKILL_RELATIVE_PATH)
            print(f"PASS ({mode}): both agents received all {len(PACKAGE_FILES)} unchanged skill files.", flush=True)
    print("Temporary projects removed. Agent invocation and writing quality were not tested.")


if __name__ == "__main__":
    main()
