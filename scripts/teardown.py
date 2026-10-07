#!/usr/bin/env python3
"""Total teardown of SEB-XRIF: wipe the machine back to a clean state.

Stops everything ``scripts/stop.py`` stops, then *removes* the Docker stacks
(containers, networks, volumes, locally built images), turns off the Tailscale
Funnel, deletes the generated artifacts (trained models, processed data,
downloaded/uploaded datasets, MLflow runs, caches, the local database, the
generated ``.env`` files and deploy secrets, and by default the Python and Node
dependency directories), and finally deletes the repository directory itself so
it can be cloned fresh from GitHub.

Typical full reset::

    python scripts/teardown.py -y      # removes everything, including this repo
    git clone <origin-url> && cd SEB-XRIF
    make up                            # or: python scripts\\run.py on Windows

Runs on Windows and POSIX with a plain Python 3 interpreter (standard library
only), so it can be shared between machines::

    python scripts/teardown.py            # Windows (asks for confirmation)
    python3 scripts/teardown.py -y        # non-interactive

Options:
    -y, --yes      do not ask for confirmation
    --dry-run      show what would be removed without removing anything
    --keep-repo    keep the repository directory (delete only the generated files)
    --keep-deps    keep .venv/ and node_modules/
    --force        kill processes on the dev ports even if they look unrelated
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEV_PORTS = {
    8000: "API (uvicorn)",
    5173: "Dashboard (Vite)",
    6006: "Storybook",
    5000: "MLflow UI",
}
ROOT_COMPOSE = ROOT / "docker-compose.yml"
DEPLOY_COMPOSE = ROOT / "deploy" / "docker-compose.yml"
DEPLOY_ENV = ROOT / "deploy" / ".env"
FUNNEL_PORT = os.environ.get("FUNNEL_PORT", "8443")
IS_WINDOWS = os.name == "nt"
OURS = ("uvicorn", "vite", "storybook", "mlflow", "api.main", "seb-xrif")

# Generated directories (relative to the repo root).
GENERATED_DIRS = [
    "mlruns",
    "mlartifacts",
    "catboost_info",
    "ui/dist",
    "ui/storybook-static",
    "web/dist",
    "web/.vite",
    "web/coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    ".dvc/tmp",
    ".dvc/cache",
    "data/raw/uploads",
    "data/raw/arete",
    "paper/assets",
]

# Dependency directories, removed unless --keep-deps.
DEP_DIRS = [".venv", "node_modules", "ui/node_modules", "web/node_modules"]

# Generated files.
GENERATED_FILES = [
    "mlflow.db",
    "sebxrif.db",
    "sebxrif.db-journal",
    ".coverage",
    ".env",
    "deploy/.env",
    "deploy/Caddyfile",
]

# Generated file globs.
GENERATED_GLOBS = [
    "models/*.joblib",
    "models/*.pkl",
    "models/*.onnx",
    "models/*.json",
    "*.onnx",
    "*.egg-info",
    "web/*.tsbuildinfo",
    "ui/*.tsbuildinfo",
    "docs/paper/*.docx",
    ".sebxrif-*.log",
]

# Locally built images to remove after `compose down`.
IMAGES = ["seb-xrif-api:local", "seb-xrif-web:local", "seb-xrif-api", "seb-xrif-web"]


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], dry: bool = False, quiet: bool = False):
    if dry:
        print(f"      $ {' '.join(cmd)}")
        return None
    if not quiet:
        print(f"      $ {' '.join(cmd)}")
    try:
        return subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError:
        return None


# --------------------------------------------------------------------------- #
# Process / port helpers (mirrors scripts/stop.py)
# --------------------------------------------------------------------------- #
def pids_listening(port: int) -> set[int]:
    pids: set[int] = set()
    if IS_WINDOWS:
        res = run(["netstat", "-ano", "-p", "tcp"], quiet=True)
        for line in (res.stdout or "").splitlines() if res else []:
            parts = line.split()
            if (
                len(parts) >= 5
                and parts[0].upper() == "TCP"
                and parts[3].upper() == "LISTENING"
                and parts[1].endswith(f":{port}")
            ):
                with contextlib.suppress(ValueError):
                    pids.add(int(parts[4]))
        return pids
    if which("lsof"):
        res = run(["lsof", "-ti", f"tcp:{port}", "-sTCP:LISTEN"], quiet=True)
        pids |= {int(x) for x in (res.stdout or "").split() if x.isdigit()}
        if pids:
            return pids
    if which("ss"):
        res = run(["ss", "-ltnp"], quiet=True)
        for line in (res.stdout or "").splitlines():
            if f":{port}" in line:
                pids |= {int(x) for x in re.findall(r"pid=(\d+)", line)}
        if pids:
            return pids
    if which("fuser"):
        res = run(["fuser", "-n", "tcp", str(port)], quiet=True)
        text = (res.stdout or "") + (res.stderr or "") if res else ""
        pids |= {int(x) for x in text.split() if x.isdigit()}
    return pids


def cmdline(pid: int) -> str:
    try:
        if IS_WINDOWS:
            res = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}')"
                    ".CommandLine",
                ],
                capture_output=True,
                text=True,
            )
            return (res.stdout or "").strip()
        if sys.platform.startswith("linux"):
            raw = Path(f"/proc/{pid}/cmdline").read_bytes()
            return raw.replace(b"\x00", b" ").decode("utf-8", "replace").strip()
        res = subprocess.run(
            ["ps", "-o", "command=", "-p", str(pid)], capture_output=True, text=True
        )
        return (res.stdout or "").strip()
    except Exception:
        return ""


def is_ours(cmd: str) -> bool:
    if not cmd:
        return True
    low = cmd.lower()
    return any(token in low for token in OURS)


def kill_pid(pid: int) -> None:
    if pid == os.getpid():
        return
    if IS_WINDOWS:
        run(["taskkill", "/PID", str(pid), "/T", "/F"], quiet=True)
        return
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(20):
        time.sleep(0.1)
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
    with contextlib.suppress(ProcessLookupError):
        os.kill(pid, signal.SIGKILL)


def stop_dev(dry: bool, force: bool) -> None:
    for port, name in DEV_PORTS.items():
        for pid in sorted(pids_listening(port)):
            cmd = cmdline(pid)
            if not force and not is_ours(cmd):
                print(f"  - skipping pid {pid} on :{port} (not SEB-XRIF: {cmd[:80]})")
                continue
            print(f"  - {name} on :{port} (pid {pid})")
            if not dry:
                kill_pid(pid)


# --------------------------------------------------------------------------- #
# Docker / Tailscale
# --------------------------------------------------------------------------- #
def compose_down(compose_file: Path, env_file: Path | None, dry: bool) -> None:
    if not compose_file.exists():
        return
    if not which("docker"):
        print("      (docker not found; skipping)")
        return
    cmd = ["docker", "compose", "-f", str(compose_file)]
    if env_file is not None and env_file.exists():
        cmd += ["--env-file", str(env_file)]
    cmd += ["down", "-v", "--remove-orphans", "--rmi", "local"]
    run(cmd, dry=dry)


def remove_images(dry: bool) -> None:
    if not which("docker"):
        return
    for image in IMAGES:
        run(["docker", "image", "rm", "-f", image], dry=dry, quiet=True)


def funnel_off(dry: bool) -> None:
    if not which("tailscale"):
        return
    run(["tailscale", "funnel", f"--https={FUNNEL_PORT}", "off"], dry=dry)


# --------------------------------------------------------------------------- #
# File removal
# --------------------------------------------------------------------------- #
def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def rm_path(p: Path, dry: bool) -> None:
    if not p.exists() and not p.is_symlink():
        return
    print(f"  - {rel(p)}")
    if dry:
        return
    if p.is_dir() and not p.is_symlink():
        try:
            shutil.rmtree(p)
        except OSError:
            # Windows: clear read-only bits and retry; ignore files still locked.
            for root, dirs, files in os.walk(p):
                for name in files + dirs:
                    with contextlib.suppress(OSError):
                        os.chmod(os.path.join(root, name), stat.S_IWRITE | stat.S_IREAD)
            shutil.rmtree(p, ignore_errors=True)
    else:
        try:
            p.unlink()
        except OSError:
            try:
                os.chmod(p, stat.S_IWRITE)
                p.unlink()
            except OSError:
                pass


def remove_artifacts(dry: bool, keep_deps: bool) -> None:
    for name in GENERATED_DIRS:
        rm_path(ROOT / name, dry)
    for name in GENERATED_FILES:
        rm_path(ROOT / name, dry)
    for pattern in GENERATED_GLOBS:
        for p in ROOT.glob(pattern):
            rm_path(p, dry)

    # data/processed/* except .gitkeep
    processed = ROOT / "data" / "processed"
    if processed.is_dir():
        for p in processed.iterdir():
            if p.name != ".gitkeep":
                rm_path(p, dry)

    # every __pycache__ in the tree (skip .git and the dependency dirs)
    skip = {".git", ".venv", "node_modules"}
    for dirpath, dirnames, _ in os.walk(ROOT, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in skip]
        if "__pycache__" in dirnames:
            rm_path(Path(dirpath) / "__pycache__", dry)
            dirnames.remove("__pycache__")

    if not keep_deps:
        for name in DEP_DIRS:
            rm_path(ROOT / name, dry)


# --------------------------------------------------------------------------- #
# Repository deletion
# --------------------------------------------------------------------------- #
def origin_url() -> str:
    res = run(["git", "remote", "get-url", "origin"], quiet=True)
    return (res.stdout or "").strip() if res else ""


def git_dirty() -> int:
    res = run(["git", "status", "--porcelain"], quiet=True)
    if not res:
        return 0
    return len([line for line in (res.stdout or "").splitlines() if line.strip()])


def is_repo_root(p: Path) -> bool:
    return (p / ".git").exists() or (p / "pyproject.toml").exists()


def try_rmtree(p: Path) -> bool:
    if not p.exists():
        return True
    try:
        shutil.rmtree(p)
    except OSError:
        return False
    return not p.exists()


def delete_repo(dry: bool) -> None:
    if not is_repo_root(ROOT):
        print(f"  - refusing to delete {ROOT}: not a git/pyproject root")
        return
    print(f"  - {ROOT}")
    if dry:
        return
    # Leave the tree first so Windows can delete the current directory.
    outside = Path(tempfile.gettempdir())
    os.chdir(outside)
    if try_rmtree(ROOT):
        return
    # Some files are still locked (typically on Windows): defer the rest to a
    # detached process that retries after this one exits.
    print("    (files locked; removing the rest after this process exits)")
    code = (
        "import shutil, sys, time\n"
        "p = sys.argv[1]\n"
        "for _ in range(120):\n"
        "    try:\n"
        "        shutil.rmtree(p)\n"
        "        break\n"
        "    except OSError:\n"
        "        time.sleep(1)\n"
    )
    kwargs: dict = {}
    if IS_WINDOWS:
        # These constants only exist on Windows; getattr keeps mypy happy and
        # the branch never runs elsewhere.
        kwargs["creationflags"] = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
            subprocess, "CREATE_NEW_PROCESS_GROUP", 0
        )
    subprocess.Popen(
        [sys.executable, "-c", code, str(ROOT)],
        cwd=str(outside),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        **kwargs,
    )


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Total teardown of SEB-XRIF.")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="do not ask for confirmation"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show what would be removed"
    )
    parser.add_argument(
        "--keep-deps", action="store_true", help="keep .venv/ and node_modules/"
    )
    parser.add_argument(
        "--keep-repo",
        action="store_true",
        help="keep the repository directory (delete only the generated files)",
    )
    parser.add_argument(
        "--force", action="store_true", help="kill dev ports even if unrelated"
    )
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    dry = args.dry_run

    print("==> SEB-XRIF total teardown")
    print("    This will remove:")
    print(
        "      - local dev servers and the Docker stacks (containers, volumes, images)"
    )
    print("      - the Tailscale Funnel listener")
    print("      - trained models, processed/uploaded/ARETE data, MLflow runs, caches")
    print("      - the local database, generated .env files and deploy secrets")
    if not args.keep_deps:
        print("      - the Python virtualenv (.venv/) and Node modules (node_modules/)")
    if args.keep_repo:
        print("    Git-tracked files are never touched.")
    else:
        print(f"      - the whole repository directory: {ROOT}")
        dirty = git_dirty()
        if dirty:
            print(f"    WARNING: {dirty} uncommitted change(s) will be lost.")

    if not args.yes and not dry:
        reply = input("    Continue? [y/N] ").strip().lower()
        if reply not in ("y", "yes"):
            print("    Aborted.")
            return 1

    url = origin_url()
    repo_name = ROOT.name

    print("\n  Stopping services:")
    compose_down(ROOT_COMPOSE, None, dry)
    compose_down(DEPLOY_COMPOSE, DEPLOY_ENV, dry)
    stop_dev(dry, args.force)
    funnel_off(dry)

    print("  Removing images:")
    remove_images(dry)

    print("  Removing generated files:")
    remove_artifacts(dry, args.keep_deps)

    if not args.keep_repo:
        print("  Deleting the repository:")
        delete_repo(dry)

    print("==> Teardown complete.")
    if args.keep_repo:
        print("    Rebuild with:  uv sync && pnpm install   (or scripts/bootstrap.sh)")
    else:
        verb = "would be removed" if dry else "was removed"
        print(f"    The repository {verb}. Restore with:")
        print(f"      git clone {url or '<origin-url>'} {repo_name}")
        print(f"      cd {repo_name}")
        print("      make up            # or: python scripts\\run.py on Windows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
