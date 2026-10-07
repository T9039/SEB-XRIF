#!/usr/bin/env python3
"""One-command startup for SEB-XRIF, on any OS.

Installs dependencies if they are missing, creates ``.env`` from
``.env.example``, trains the default model if no artifact exists, then runs the
API (:8000) and the dashboard (:5173) together until you press Ctrl+C.

This is the single implementation behind ``make up`` and the Windows
double-click path, so there is no separate shell/``.cmd`` script per platform::

    python scripts/run.py            # Windows
    python3 scripts/run.py           # Linux / macOS
    make up                          # shortcut
    make up ARGS='--no-train'        # skip training

Options:
    --no-train   skip training the default model
    PORT=9000    environment variable: API port (dashboard stays on 5173)
"""

from __future__ import annotations

import argparse
import contextlib
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = os.name == "nt"
API_PORT = int(os.environ.get("PORT", "8000"))
WEB_PORT = 5173
MODEL = ROOT / "models" / "model.joblib"


def need(name: str) -> None:
    if shutil.which(name) is None:
        print(
            f"!! '{name}' is not installed. See the Prerequisites section of README.md."
        )
        raise SystemExit(1)


def port_busy(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def wrap(cmd: list[str]) -> list[str]:
    """Resolve the executable, routing Windows .cmd/.bat shims through cmd.exe."""
    exe = shutil.which(cmd[0])
    if not exe:
        return cmd
    if IS_WINDOWS and exe.lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", exe, *cmd[1:]]
    return [exe, *cmd[1:]]


def run(cmd: list[str], check: bool = True) -> int:
    print(f"==> {' '.join(cmd)}")
    try:
        return subprocess.run(wrap(cmd), cwd=str(ROOT)).returncode
    except FileNotFoundError:
        print(f"!! Could not run '{cmd[0]}'.", file=sys.stderr)
        if check:
            raise SystemExit(1) from None
        return 1


def bootstrap() -> None:
    need("uv")
    need("node")
    need("pnpm")
    run(["uv", "sync"])
    run(["uv", "run", "pre-commit", "install"], check=False)
    create_env()
    run(["pnpm", "install"])


def create_env() -> None:
    env = ROOT / ".env"
    if not env.exists():
        shutil.copy(ROOT / ".env.example", env)
        print("==> Created .env from .env.example")


def spawn(cmd: list[str], cwd: Path) -> subprocess.Popen:
    kwargs: dict = {}
    if IS_WINDOWS:
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(wrap(cmd), cwd=str(cwd), **kwargs)


def _on_signal(signum: int, frame: object) -> None:
    # Turn SIGTERM (e.g. `kill`, or `timeout`) into the same path as Ctrl+C.
    raise KeyboardInterrupt


def terminate(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    if IS_WINDOWS:
        subprocess.run(
            ["taskkill", "/PID", str(proc.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return
    with contextlib.suppress(ProcessLookupError):
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        with contextlib.suppress(ProcessLookupError):
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SEB-XRIF (API + dashboard).")
    parser.add_argument(
        "--no-train", action="store_true", help="skip training the default model"
    )
    args = parser.parse_args(argv)

    os.chdir(ROOT)

    print("==> Checking prerequisites")
    need("uv")
    need("node")
    need("pnpm")

    for port, label in ((WEB_PORT, "dashboard"), (API_PORT, "API")):
        if port_busy(port):
            print(f"!! Port {port} ({label}) is already in use.", file=sys.stderr)
            print(
                "   Stop the process using it (or set PORT=... for the API) and retry.",
                file=sys.stderr,
            )
            return 1

    if not (ROOT / ".venv").is_dir() or not (ROOT / "node_modules").is_dir():
        print("==> Missing dependencies; running bootstrap")
        bootstrap()
    else:
        create_env()

    if not args.no_train and not MODEL.exists():
        print("==> No model found; training the default Random Forest")
        run(["uv", "run", "python", "-m", "analytics.train", "--no-mlflow"])

    print()
    print("=" * 62)
    print(" SEB-XRIF is starting")
    print(f"   Dashboard : http://localhost:{WEB_PORT}")
    print(f"   API docs  : http://localhost:{API_PORT}/docs")
    print("   Stop      : Ctrl+C")
    print("=" * 62)
    print()

    if not IS_WINDOWS:
        signal.signal(signal.SIGTERM, _on_signal)

    api: subprocess.Popen | None = None
    web: subprocess.Popen | None = None
    try:
        api = spawn(
            [
                "uv",
                "run",
                "uvicorn",
                "api.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                str(API_PORT),
            ],
            ROOT,
        )
        web = spawn(["pnpm", "run", "dev"], ROOT / "web")
        while api.poll() is None and web.poll() is None:
            time.sleep(0.5)
        print("!! A server exited; shutting the other one down.")
    except KeyboardInterrupt:
        print("\n==> Stopping")
    finally:
        terminate(api)
        terminate(web)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
