"""Generate paper/sections/references.md from the group reference list.

The single source of truth for the bibliography is
``docs/paper/build_section3_docx.py`` (the ``REFERENCES`` list) so the paper and
the Word draft cannot diverge. The list is read with ``ast`` rather than imported,
so this tool does not need ``python-docx`` installed.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs" / "paper" / "build_section3_docx.py"
OUT = ROOT / "paper" / "sections" / "references.md"


def load_references(path: Path) -> list[str]:
    """Extract the module-level ``REFERENCES`` constant without importing it."""
    module = ast.parse(path.read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "REFERENCES":
                    value = ast.literal_eval(node.value)
                    return [str(item) for item in value]
    raise SystemExit(f"REFERENCES not found in {path}")


def main() -> None:
    references = load_references(SOURCE)
    lines = ["# References", ""]
    for index, reference in enumerate(references, start=1):
        lines.append(f"[{index}] {' '.join(reference.split())}")
        lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT} ({len(references)} references)")


if __name__ == "__main__":
    main()
