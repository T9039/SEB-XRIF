"""Longitudinal evaluation summary read from the evaluation store.

The DUT pilot (or a demonstration import) writes T0/T1/T2 scores and SUS rows
through ``eval.report --store``. This module turns those rows back into the
fixed protocol summary the dashboard shows, tagged by source so example data
and real pilot data never blur together.
"""

from __future__ import annotations

from typing import Any

from eval.longitudinal import COHEN_D_BENCHMARK, SUS_BENCHMARK, summarise

from .config import Settings, get_settings
from .db import evaluations_frame, get_engine


def evaluation_summary(
    settings: Settings | None = None,
    url: str | None = None,
    source: str | None = None,
) -> dict[str, Any]:
    """Return the usability and learning/retention summary for the store."""
    settings = settings or get_settings()
    engine = get_engine(url or settings.resolve_database_url())
    try:
        frame = evaluations_frame(engine)
    except Exception:  # noqa: BLE001 - missing table means nothing imported yet
        return {"available": False, "reason": "No pilot data imported yet."}

    if frame.empty:
        return {"available": False, "reason": "No pilot data imported yet."}
    if source:
        frame = frame[frame["source"] == source]
    if frame.empty:
        return {
            "available": False,
            "reason": f"No evaluation data for source '{source}'.",
        }

    summary: dict[str, Any] = {
        "available": True,
        "sources": sorted(str(value) for value in frame["source"].unique()),
        "records": int(len(frame)),
        "benchmarks": {"sus": SUS_BENCHMARK, "cohens_d": COHEN_D_BENCHMARK},
    }

    sus = frame[frame["measure"] == "sus"]["value"]
    if not sus.empty:
        mean = float(sus.mean())
        summary["usability"] = {
            "n": int(len(sus)),
            "mean": round(mean, 2),
            "benchmark": SUS_BENCHMARK,
            "meets_benchmark": mean >= SUS_BENCHMARK,
        }

    points = {
        time_point: frame[
            (frame["measure"] == "score") & (frame["time_point"] == time_point)
        ]["value"].tolist()
        for time_point in ("T0", "T1", "T2")
    }
    if points["T0"] and points["T1"]:
        count = min(len(points["T0"]), len(points["T1"]))
        t0 = points["T0"][:count]
        t1 = points["T1"][:count]
        t2 = points["T2"][:count] if points["T2"] else None
        if t2 is not None:
            t0 = t0[: len(t2)]
            t1 = t1[: len(t2)]
        summary["learning"] = summarise(t0, t1, t2)
    return summary


def import_report(
    payload: dict[str, Any],
    *,
    source: str,
    url: str | None = None,
) -> dict[str, int]:
    """Store an evaluation payload (as used by ``eval.report --store``)."""
    from eval.report import _store

    return _store(payload, url, source)
