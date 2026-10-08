#!/usr/bin/env python3
"""Verify the framework reproduces from a clean checkout.

Copies the tracked tree (working-tree contents, so uncommitted edits are
included) into a temporary directory with no DVC cache, re-runs the pipeline
there, and fails if the regenerated ``dvc.lock`` differs from the committed one.
A difference means the recorded data/model artifacts no longer match the
sources that are supposed to produce them.

Works on Windows, Linux, and macOS::

    uv run python scripts/repro_check.py
"""

from __future__ import annotations

import difflib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _common import ROOT, need


def export_tracked_tree(dest: Path) -> None:
    tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    for raw in tracked.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8")
        source = ROOT / rel
        if not source.exists():
            print(f"   (skipping missing tracked file {rel})", file=sys.stderr)
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def seed_history(work: Path) -> None:
    """DVC needs an SCM context; give the export a throwaway local history."""
    git = [
        "git",
        "-c",
        "user.email=repro-check@localhost",
        "-c",
        "user.name=repro-check",
    ]
    subprocess.run(["git", "init", "-q"], cwd=work, check=True)
    subprocess.run([*git, "add", "-A"], cwd=work, check=True)
    subprocess.run([*git, "commit", "-qm", "repro-check export"], cwd=work, check=True)


def main() -> int:
    lock = ROOT / "dvc.lock"
    if not lock.is_file():
        print("!! No dvc.lock found at the repo root.", file=sys.stderr)
        return 2

    need("uv")
    lock_before = lock.read_bytes()
    work = Path(tempfile.mkdtemp(prefix="sebxrif-repro-"))
    try:
        print(f"==> Exporting the tracked tree to {work}")
        export_tracked_tree(work)
        seed_history(work)

        print("==> Reproducing the pipeline from a clean checkout")
        env = os.environ.copy()
        env["UV_PROJECT"] = str(work)
        env["UV_PROJECT_ENVIRONMENT"] = str(ROOT / ".venv")
        code = subprocess.run(
            ["uv", "run", "--frozen", "dvc", "repro"], cwd=work, env=env
        ).returncode
        if code:
            return code

        print("==> Comparing the regenerated lock to the committed lock")
        regenerated = (work / "dvc.lock").read_bytes()
        if regenerated == lock_before:
            print(
                "==> Reproducible: the regenerated dvc.lock matches the committed graph"
            )
            return 0

        print(
            "!! Reproduction drifted from the committed lock (diff above).",
            file=sys.stderr,
        )
        for line in difflib.unified_diff(
            lock_before.decode("utf-8").splitlines(),
            regenerated.decode("utf-8").splitlines(),
            fromfile="committed/dvc.lock",
            tofile="regenerated/dvc.lock",
            lineterm="",
        ):
            print(line, file=sys.stderr)
        print(
            "   Run 'uv run dvc repro' in the repo root and commit dvc.lock.",
            file=sys.stderr,
        )
        return 1
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
