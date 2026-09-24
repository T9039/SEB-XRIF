"""Server-side aggregation and derived statistics over the learner data.

Powers the dashboard's Chart Studio and the derived-stat panels. All heavy
lifting happens here in pandas so the browser only renders.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import Settings
from .data import read_learners
from .schema import CATEGORICAL

TARGET = "Class"
AGGREGATES = ("mean", "sum", "median", "min", "max", "count")


def column_metadata(settings: Settings | None = None) -> dict[str, Any]:
    """Return each column's kind and, for categoricals, its option set."""
    frame, source = read_learners(settings)
    columns: list[dict[str, Any]] = []
    for name in frame.columns:
        series = frame[name]
        if name in CATEGORICAL or name == TARGET or series.dtype == object:
            columns.append(
                {
                    "name": name,
                    "kind": "categorical",
                    "options": sorted(str(value) for value in series.dropna().unique()),
                }
            )
        else:
            columns.append(
                {
                    "name": name,
                    "kind": "numeric",
                    "min": float(series.min()),
                    "max": float(series.max()),
                    "mean": round(float(series.mean()), 3),
                }
            )
    return {"data_source": source, "target": TARGET, "columns": columns}


def run_query(
    x: str,
    y: str | None = None,
    group: str | None = None,
    aggregate: str = "mean",
    filters: dict[str, str] | None = None,
    limit: int = 100,
    sort: str = "x",
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Group the learner table and return a chart-ready wide table."""
    frame, source = read_learners(settings)
    data = frame.copy()

    for column, value in (filters or {}).items():
        if value and value not in ("all", ""):
            if column not in data.columns:
                raise KeyError(column)
            data = data[data[column].astype(str) == str(value)]

    if x not in data.columns:
        raise KeyError(x)
    if y is not None and y not in data.columns:
        raise KeyError(y)
    if aggregate not in AGGREGATES:
        raise ValueError(f"aggregate must be one of {AGGREGATES}")

    keys = [x, *([group] if group else [])]
    if y and aggregate != "count":
        grouped = data.groupby(keys, observed=True)[y].agg(aggregate)
    else:
        grouped = data.groupby(keys, observed=True).size()

    table = grouped.reset_index(name="value")
    if sort == "value":
        table = table.sort_values("value", ascending=False)
    elif sort == "value_asc":
        table = table.sort_values("value", ascending=True)
    else:
        table = table.sort_values(by=keys)
    table = table.head(limit)

    if group:
        wide = table.pivot_table(
            index=x, columns=group, values="value", aggfunc="first"
        )
        series = [str(column) for column in wide.columns]
        rows: list[dict[str, Any]] = []
        for index, row in wide.iterrows():
            entry: dict[str, Any] = {"x": str(index)}
            for name in series:
                value = row.get(name)
                entry[name] = None if pd.isna(value) else round(float(value), 4)
            rows.append(entry)
    else:
        series = [y or "count"]
        rows = [
            {"x": str(record[x]), "value": round(float(record["value"]), 4)}
            for _, record in table.iterrows()
        ]

    return {
        "data_source": source,
        "x": x,
        "y": y,
        "group": group,
        "aggregate": "count" if aggregate == "count" or not y else aggregate,
        "series": series,
        "rows": rows,
        "total": int(len(data)),
    }


def correlation(settings: Settings | None = None) -> dict[str, Any]:
    """Return the Pearson correlation matrix of the numeric predictors."""
    frame, source = read_learners(settings)
    numeric = frame.select_dtypes(include="number")
    matrix = numeric.corr().round(3)
    return {
        "data_source": source,
        "columns": [str(column) for column in matrix.columns],
        "matrix": matrix.values.tolist(),
    }


def distribution(
    column: str, bins: int = 10, settings: Settings | None = None
) -> dict[str, Any]:
    """Return a value-count (categorical) or histogram (numeric) for a column."""
    frame, source = read_learners(settings)
    if column not in frame.columns:
        raise KeyError(column)
    series = frame[column]

    if column in CATEGORICAL or column == TARGET or series.dtype == object:
        counts = series.astype(str).value_counts().sort_index()
        return {
            "data_source": source,
            "column": column,
            "kind": "categorical",
            "rows": [{"x": key, "value": int(value)} for key, value in counts.items()],
        }

    values = series.astype(float)
    histogram, edges = np.histogram(values, bins=bins)
    rows = [
        {
            "x": f"{edges[index]:.1f}-{edges[index + 1]:.1f}",
            "value": int(histogram[index]),
        }
        for index in range(len(histogram))
    ]
    return {
        "data_source": source,
        "column": column,
        "kind": "numeric",
        "rows": rows,
    }
