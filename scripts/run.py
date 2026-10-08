#!/usr/bin/env python3
"""One-command startup for SEB-XRIF, on any OS.

Installs dependencies if they are missing, creates ``.env`` from
``.env.example``, trains the default model if no artifact exists, then runs the
API (:8000) and the dashboard (:5173) together.

By default it stays in the foreground and serves until you press Ctrl+C (the
API is waited on before the dashboard starts, so the first page load does not
fail). Pass ``--detach`` (``-d``) to start both in the background and get your
shell back; stop them with ``scripts/stop.py`` (``make stop``).

This is the single implementation behind ``make up``, so there is no separate
shell/``.cmd`` script per platform::

    python scripts/run.py            # Windows
    python3 scripts/run.py           # Linux / macOS
    make up                          # shortcut
    make up ARGS='--no-train'        # skip training
    make up ARGS='--detach'          # background

Options:
    -d, --detach  start in the background and return (logs: .sebxrif-*.log)
    --no-train    skip training the default model
    PORT=9000     environment variable: API port (dashboard stays on 5173)
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
IS_WINDOWS = os.name == "nt"
API_PORT = int(os.environ.get("PORT", "8000"))
WEB_PORT = 5173
MODEL = ROOT / "models" / "model.joblib"
API_LOG = ROOT / ".sebxrif-api.log"
WEB_LOG = ROOT / ".sebxrif-web.log"


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


def api_ready(port: int) -> bool:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/health", timeout=2
        ) as resp:
            return resp.status == 200
    except Exception:
        return False


def wait_for_api(port: int, timeout: float = 90.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if api_ready(port):
            return True
        time.sleep(0.5)
    return False


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


def web_cmd() -> list[str]:
    """Mirror web/package.json's "dev" script through `pnpm exec`.

    `pnpm exec` runs the binary directly instead of through pnpm's lifecycle
    wrapper, which avoids the "[ELIFECYCLE] Command failed." noise pnpm prints
    when the dev server is stopped by a signal.
    """
    script = "vp dev"
    try:
        pkg = json.loads((ROOT / "web" / "package.json").read_text(encoding="utf-8"))
        script = pkg.get("scripts", {}).get("dev", script)
    except Exception:
        pass
    return ["pnpm", "exec", *script.split()]


def spawn(
    cmd: list[str],
    cwd: Path,
    stdout: Any = None,
    stderr: Any = None,
    detach: bool = False,
) -> subprocess.Popen:
    kwargs: dict = {}
    if IS_WINDOWS:
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        if detach:
            flags |= getattr(subprocess, "DETACHED_PROCESS", 0)
        kwargs["creationflags"] = flags
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(
        wrap(cmd), cwd=str(cwd), stdout=stdout, stderr=stderr, **kwargs
    )


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


def api_command() -> list[str]:
    # Watch only the application packages. Without this, uvicorn's reloader
    # watches the whole tree -- including .venv and node_modules -- so package
    # or editor churn triggers reload loops (especially on Windows).
    return [
        "uv",
        "run",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--reload-dir",
        "api",
        "--reload-dir",
        "analytics",
        "--reload-dir",
        "eval",
        "--host",
        "0.0.0.0",
        "--port",
        str(API_PORT),
    ]


def banner(running: bool) -> None:
    print()
    print("=" * 62)
    print(" SEB-XRIF is running" if running else " SEB-XRIF is up")
    print(f"   Dashboard : http://localhost:{WEB_PORT}")
    print(f"   API docs  : http://localhost:{API_PORT}/docs")
    if running:
        print(f"   Logs      : {API_LOG.name}, {WEB_LOG.name}")
        print("   Stop      : python scripts/stop.py   (or: make stop)")
    else:
        print("   Stop      : Ctrl+C")
    print("=" * 62)
    print()


def run_detached() -> int:
    with open(API_LOG, "ab") as api_log, open(WEB_LOG, "ab") as web_log:
        api = spawn(
            api_command(), ROOT, stdout=api_log, stderr=subprocess.STDOUT, detach=True
        )
        if not wait_for_api(API_PORT):
            print(
                f"!! The API did not become ready. See {API_LOG.name}.", file=sys.stderr
            )
            terminate(api)
            return 1
        spawn(
            web_cmd(),
            ROOT / "web",
            stdout=web_log,
            stderr=subprocess.STDOUT,
            detach=True,
        )
        time.sleep(1.5)
    banner(running=True)
    return 0


def run_foreground() -> int:
    if not IS_WINDOWS:
        signal.signal(signal.SIGTERM, _on_signal)
    api: subprocess.Popen | None = None
    web: subprocess.Popen | None = None
    try:
        print(f"==> Starting the API on :{API_PORT}")
        api = spawn(api_command(), ROOT)
        if not wait_for_api(API_PORT):
            print("!! The API did not become ready in time.", file=sys.stderr)
            return 1
        print(f"==> Starting the dashboard on :{WEB_PORT}")
        web = spawn(web_cmd(), ROOT / "web")
        banner(running=False)
        while api.poll() is None and web.poll() is None:
            time.sleep(0.5)
        print("!! A server exited; shutting the other one down.")
    except KeyboardInterrupt:
        print("\n==> Stopping")
    finally:
        terminate(web)
        terminate(api)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SEB-XRIF (API + dashboard).")
    parser.add_argument(
        "-d",
        "--detach",
        action="store_true",
        help="start in the background and return (logs: .sebxrif-*.log)",
    )
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

    if args.detach:
        return run_detached()
    return run_foreground()


if __name__ == "__main__":
    raise SystemExit(main())
