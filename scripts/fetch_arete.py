"""Download the ARETE XR xAPI pilots and verify their pinned checksums.

The pilots are external CC BY 4.0 data; they are downloaded rather than
committed. Checksums live in ``analytics/xr.py`` so a changed upstream file is
rejected instead of silently analysed.

Examples:
    uv run python scripts/fetch_arete.py
    uv run python scripts/fetch_arete.py pbis
"""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics.config import get_settings  # noqa: E402
from analytics.xr import PILOTS, sha256_of  # noqa: E402


def fetch(name: str, out_dir: Path, force: bool = False) -> Path:
    """Download one pilot into ``out_dir`` and verify its checksum."""
    pilot = PILOTS[name]
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / pilot.filename
    if dest.exists() and not force:
        if sha256_of(dest) == pilot.sha256:
            print(f"ok   {pilot.filename} (cached)")
            return dest
        print(f"stale {pilot.filename}; re-downloading")

    print(f"get  {pilot.filename} <- {pilot.url}")
    urllib.request.urlretrieve(pilot.url, dest)
    digest = sha256_of(dest)
    if digest != pilot.sha256:
        dest.unlink(missing_ok=True)
        raise SystemExit(f"checksum mismatch for {pilot.filename}: {digest}")
    print(f"ok   {pilot.filename}")
    return dest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Download ARETE pilots.")
    parser.add_argument(
        "pilots",
        nargs="*",
        default=None,
        help="Pilot names to fetch (default: all).",
    )
    parser.add_argument("--force", action="store_true", help="Re-download if cached.")
    args = parser.parse_args(argv)

    names = args.pilots or list(PILOTS)
    unknown = [name for name in names if name not in PILOTS]
    if unknown:
        known = ", ".join(PILOTS)
        raise SystemExit(f"Unknown pilots: {', '.join(unknown)}. Known: {known}")

    out_dir = get_settings().arete_raw_dir
    for name in names:
        fetch(name, out_dir, force=args.force)


if __name__ == "__main__":
    main()
