"""Feature and end-to-end tests for the paper pipeline (Markdown -> Typst)."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER = REPO_ROOT / "paper"
TOOL = PAPER / "tools" / "make_references.py"


def _load_reference_tool():
    spec = importlib.util.spec_from_file_location("make_references", TOOL)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------- feature
def test_references_are_extracted():
    tool = _load_reference_tool()
    references = tool.load_references(tool.SOURCE)
    assert len(references) == 37
    assert all(isinstance(item, str) and item for item in references)


def test_reference_file_matches_source():
    generated = (PAPER / "sections" / "references.md").read_text(encoding="utf-8")
    assert generated.startswith("# References")
    assert "[1]" in generated
    assert "[37]" in generated


def test_sections_referenced_by_main_exist():
    main = (PAPER / "main.typ").read_text(encoding="utf-8")
    for line in main.splitlines():
        marker = 'md("sections/'
        if marker in line:
            rel = line.split(marker, 1)[1].split('"', 1)[0]
            assert (PAPER / "sections" / rel).exists(), rel


# ------------------------------------------------------------------------- e2e
@pytest.mark.skipif(shutil.which("typst") is None, reason="typst not installed")
def test_paper_builds_to_pdf():
    completed = subprocess.run(
        [str(PAPER / "build.sh")],
        cwd=PAPER,
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    pdf = PAPER / "main.pdf"
    assert pdf.exists()
    assert pdf.stat().st_size > 10_000

    pdfinfo = shutil.which("pdfinfo")
    if pdfinfo:
        info = subprocess.run(
            [pdfinfo, str(pdf)], capture_output=True, text=True, check=False
        )
        pages = [line for line in info.stdout.splitlines() if line.startswith("Pages:")]
        assert pages and int(pages[0].split()[-1]) >= 1
