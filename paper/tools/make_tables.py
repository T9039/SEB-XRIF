"""Generate the paper's data tables from the reports directory.

Standard library only, so the paper can be rebuilt on a runner that has Typst but
not the full Python environment.

Examples:
    python3 paper/tools/make_tables.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"
SECTIONS = ROOT / "paper" / "sections"


def _write(name: str, text: str) -> None:
    SECTIONS.mkdir(parents=True, exist_ok=True)
    (SECTIONS / name).write_text(text, encoding="utf-8")
    print(f"Wrote paper/sections/{name}")


def results_table() -> None:
    source = REPORTS / "results.md"
    if source.exists():
        _write("results_table.md", source.read_text(encoding="utf-8"))
    else:
        _write(
            "results_table.md",
            "_Results table not generated yet. Run `make matrix`._\n",
        )


def tuning_table() -> None:
    lines = [
        "### Tuned configurations",
        "",
        "| Model | Best CV macro F1 | Best parameters |",
        "| --- | --- | --- |",
    ]
    source = REPORTS / "tuning.json"
    if source.exists():
        data = json.loads(source.read_text(encoding="utf-8"))
        for model, payload in data.items():
            value = payload.get("best_value")
            value_text = f"{value:.4f}" if isinstance(value, (int, float)) else "—"
            params = payload.get("best_params", {})
            params_text = (
                ", ".join(f"{key}={val}" for key, val in params.items()) or "—"
            )
            lines.append(f"| {model} | {value_text} | {params_text} |")
    else:
        lines.append("| _run `make tune`_ | — | — |")
    lines.append("")
    _write("tuning_table.md", "\n".join(lines))


def explain_table() -> None:
    lines = [
        "### Most stable feature drivers (cross-fold permutation importance)",
        "",
        "| Feature | Mean | Std |",
        "| --- | --- | --- |",
    ]
    source = REPORTS / "explain.json"
    if source.exists():
        data = json.loads(source.read_text(encoding="utf-8"))
        features = data.get("cross_fold", {}).get("features", [])[:10]
        for item in features:
            lines.append(
                f"| {item['feature']} | {item['mean']:.4f} | {item['std']:.4f} |"
            )
    else:
        lines.append("| _run `python -m analytics.explain`_ | — | — |")
    lines.append("")
    _write("explain_table.md", "\n".join(lines))


def main() -> None:
    results_table()
    tuning_table()
    explain_table()


if __name__ == "__main__":
    main()
