#!/usr/bin/env python3
"""Stop all SEB-XRIF services.

Stops the local dev servers (API, dashboard, Storybook, MLflow), the Docker
Compose stacks (root and deploy), and the Tailscale Funnel listener.

Non-destructive: containers and volumes are only *stopped*, never removed, and
no generated files are deleted. Use ``scripts/teardown.py`` to remove
everything.

Runs on Windows and POSIX with a plain Python 3 interpreter (standard library
only), so it can be shared between machines::

    python scripts/stop.py            # Windows
    python3 scripts/stop.py           # Linux / macOS

Options:
    --dry-run     show what would be stopped without doing it
    --no-dev      skip the local dev servers
    --no-docker   skip the Docker Compose stacks
    --no-funnel   skip the Tailscale Funnel
    --force       kill processes on the dev ports even if they do not look
                  like SEB-XRIF processes
"""

from __future__ import annotations

import argparse
import contextlib
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Local dev servers started by scripts/run.sh, scripts/dev.sh, make mlflow,
# make storybook.  Docker publishes other ports (8000/8080/5000/...); those are
# handled by the Compose stack, which is stopped first so it cannot be
# mistaken for a dev process.
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

# Substrings that mark a process as belonging to this project.
OURS = ("uvicorn", "vite", "storybook", "mlflow", "api.main", "seb-xrif")


def which(name: str) -> str | None:
    return shutil.which(name)


def run(cmd: list[str], dry: bool = False, quiet: bool = False):
    """Run a command in the repo root. Returns CompletedProcess or None."""
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
# Process / port helpers
# --------------------------------------------------------------------------- #
def pids_listening(port: int) -> set[int]:
    """Return the PIDs with a TCP listener on *port* (best effort, cross-platform)."""
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

    # POSIX: try lsof, then ss, then fuser.
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
    """Best-effort command line for *pid* (empty string if unavailable)."""
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
            ["ps", "-o", "command=", "-p", str(pid)],
            capture_output=True,
            text=True,
        )
        return (res.stdout or "").strip()
    except Exception:
        return ""


def is_ours(cmd: str) -> bool:
    if not cmd:
        return True  # cannot tell; the ports are project-specific, assume ours
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
        pids = pids_listening(port)
        if not pids:
            continue
        for pid in sorted(pids):
            cmd = cmdline(pid)
            if not force and not is_ours(cmd):
                print(
                    f"  - skipping pid {pid} on :{port} "
                    f"(not a SEB-XRIF process: {cmd[:80]})"
                )
                continue
            print(f"  - {name} on :{port} (pid {pid})")
            if not dry:
                kill_pid(pid)


# --------------------------------------------------------------------------- #
# Docker / Tailscale
# --------------------------------------------------------------------------- #
def compose_stop(
    compose_file: Path, env_file: Path | None, dry: bool, action: str = "stop", extra=()
) -> None:
    if not compose_file.exists():
        return
    if not which("docker"):
        print("      (docker not found; skipping)")
        return
    cmd = ["docker", "compose", "-f", str(compose_file)]
    if env_file is not None and env_file.exists():
        cmd += ["--env-file", str(env_file)]
    cmd += [action, *extra]
    run(cmd, dry=dry)


def funnel_off(dry: bool) -> None:
    if not which("tailscale"):
        print("      (tailscale not found; skipping)")
        return
    run(["tailscale", "funnel", f"--https={FUNNEL_PORT}", "off"], dry=dry)


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stop all SEB-XRIF services.")
    parser.add_argument(
        "--dry-run", action="store_true", help="show what would be stopped"
    )
    parser.add_argument("--no-dev", action="store_true", help="skip local dev servers")
    parser.add_argument(
        "--no-docker", action="store_true", help="skip Docker Compose stacks"
    )
    parser.add_argument(
        "--no-funnel", action="store_true", help="skip Tailscale Funnel"
    )
    parser.add_argument(
        "--force", action="store_true", help="kill dev ports even if unrelated"
    )
    args = parser.parse_args(argv)

    os.chdir(ROOT)
    dry = args.dry_run
    print(f"==> Stopping SEB-XRIF{' (dry run)' if dry else ''}")

    if not args.no_docker:
        print("  Docker stacks:")
        compose_stop(ROOT_COMPOSE, None, dry)
        compose_stop(DEPLOY_COMPOSE, DEPLOY_ENV, dry)

    if not args.no_dev:
        print("  Local dev servers:")
        stop_dev(dry, args.force)

    if not args.no_funnel:
        print("  Tailscale Funnel:")
        funnel_off(dry)

    print("==> Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
