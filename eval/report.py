"""Evaluation report: usability (SUS), effect sizes, and T0/T1/T2 retention.

Combines the framework's fixed measures into a single report and Markdown
template. The same protocol every adopter must run, in one place.

Examples:
    uv run python -m eval.report --input pilot.json
    uv run python -m eval.report --input pilot.json --store
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from .longitudinal import (
    COHEN_D_BENCHMARK,
    COHEN_THRESHOLDS,
    SUS_BENCHMARK,
    summarise,
)
from .sus import sus_score


def _mean(values: Sequence[float]) -> float:
    return float(sum(values) / len(values)) if values else 0.0


def build_report(
    sus_responses: Sequence[Sequence[int]] | None = None,
    t0: Sequence[float] | None = None,
    t1: Sequence[float] | None = None,
    t2: Sequence[float] | None = None,
    source: str = "example",
) -> dict[str, Any]:
    """Build the evaluation report from raw responses and time-point scores."""
    report: dict[str, Any] = {
        "source": source,
        "benchmarks": {
            "sus": SUS_BENCHMARK,
            "cohens_d": COHEN_D_BENCHMARK,
            "thresholds": COHEN_THRESHOLDS,
        },
    }

    if sus_responses:
        scores = [sus_score(list(responses)) for responses in sus_responses]
        average = _mean(scores)
        report["usability"] = {
            "n": len(scores),
            "scores": scores,
            "mean": round(average, 2),
            "benchmark": SUS_BENCHMARK,
            "meets_benchmark": average >= SUS_BENCHMARK,
        }

    if t0 and t1:
        learning = summarise(t0, t1, t2)
        learning["meets_immediate_benchmark"] = (
            learning["d_immediate"] >= COHEN_D_BENCHMARK
        )
        report["learning"] = learning

    return report


def to_markdown(report: dict[str, Any]) -> str:
    """Render the report as Markdown for the paper's evaluation section."""
    benchmarks = report["benchmarks"]
    lines = [
        "# Evaluation report",
        "",
        f"Benchmarks: SUS {benchmarks['sus']}, Cohen's d {benchmarks['cohens_d']} "
        f"(small/medium/large {benchmarks['thresholds']['small']}/"
        f"{benchmarks['thresholds']['medium']}/{benchmarks['thresholds']['large']}).",
        "",
    ]

    if "usability" in report:
        usability = report["usability"]
        lines += [
            "## Usability (SUS)",
            "",
            f"- Participants: {usability['n']}",
            f"- Mean SUS: {usability['mean']} (benchmark {usability['benchmark']})",
            f"- Meets benchmark: {'yes' if usability['meets_benchmark'] else 'no'}",
            "",
        ]

    if "learning" in report:
        learning = report["learning"]
        summary = f"- Mean T0: {learning['mean_t0']:.2f}, T1: {learning['mean_t1']:.2f}"
        if "mean_t2" in learning:
            summary += f", T2: {learning['mean_t2']:.2f}"
        lines += [
            "## Learning and retention",
            "",
            f"- Participants: {learning['n']}",
            summary,
            f"- Immediate gain: {learning['gain_immediate']:.2f} "
            f"(Cohen's d = {learning['d_immediate']:.3f})",
        ]
        if "d_delayed" in learning:
            lines += [
                f"- Delayed gain (T2 vs T0): {learning['gain_delayed']:.2f} "
                f"(d = {learning['d_delayed']:.3f})",
                f"- Decay (T2 vs T1): {learning['decay_t2_t1']:.2f} "
                f"(d = {learning['d_decay']:.3f})",
                f"- Retention ratio: {learning['retention_ratio']}",
            ]
        lines.append("")

    lines += [
        "## Protocol",
        "",
        "T0 baseline, T1 immediately after the XR module, T2 one semester later "
        "with no re-teaching. T2 is reported as scheduled or future when it has "
        "not yet been measured.",
        "",
    ]
    return "\n".join(lines)


def _store(payload: dict[str, Any], url: str | None, source: str) -> dict[str, int]:
    """Persist the raw measurements to the application database."""
    from analytics.db import get_engine, record_evaluation, session_scope

    engine = get_engine(url)
    stored = {"scores": 0, "sus": 0}
    with session_scope(engine) as session:
        for time_point in ("t0", "t1", "t2"):
            for value in payload.get(time_point) or []:
                record_evaluation(
                    session, time_point.upper(), "score", float(value), source=source
                )
                stored["scores"] += 1
        for responses in payload.get("sus") or []:
            record_evaluation(
                session,
                "T1",
                "sus",
                sus_score(list(responses)),
                source=source,
            )
            stored["sus"] += 1
    return stored


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build an evaluation report.")
    parser.add_argument(
        "--input", type=Path, required=True, help="JSON with sus/t0/t1/t2."
    )
    parser.add_argument("--out", type=Path, default=Path("reports/evaluation.md"))
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--store", action="store_true", help="Persist to the database.")
    parser.add_argument("--url", default=None, help="Database URL for --store.")
    parser.add_argument(
        "--source",
        default="example",
        help="Provenance tag for stored measurements (e.g. pilot, example).",
    )
    args = parser.parse_args(argv)

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    report = build_report(
        payload.get("sus"),
        payload.get("t0"),
        payload.get("t1"),
        payload.get("t2"),
        source=args.source,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(to_markdown(report), encoding="utf-8")
    json_out = args.json_out or args.out.with_suffix(".json")
    json_out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out} and {json_out}")

    if args.store:
        stored = _store(payload, args.url, args.source)
        print(f"Stored {stored['scores']} scores and {stored['sus']} SUS rows")


if __name__ == "__main__":
    main()
