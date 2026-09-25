"""Full comparison-matrix benchmark.

Trains every model in the catalog, evaluates each with a held-out split and
stratified k-fold cross-validation, and writes the evidence used by the paper:
``reports/results.csv``, ``reports/results.md``, and a comparison figure.

Examples:
    uv run python -m analytics.benchmark --all
    uv run python -m analytics.benchmark --models random_forest svc knn
    uv run python -m analytics.benchmark --all --cv 10
"""

from __future__ import annotations

import argparse
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import pandas as pd

from .config import Settings, get_settings
from .data import features_and_target, load_source, split
from .evaluate import classification_metrics, cross_validate_model
from .models import build_pipeline, model_catalog

#: Published ensemble benchmark for the xAPI dataset (Amrieh et al., 2016).
BENCHMARK_ACCURACY = (0.75, 0.83)

METRIC_COLUMNS = [
    "model",
    "status",
    "accuracy",
    "precision_macro",
    "recall_macro",
    "f1_macro",
    "f1_weighted",
    "roc_auc_ovr",
    "cv_mean",
    "cv_std",
    "cv_ci_low",
    "cv_ci_high",
    "fit_seconds",
    "n_train",
    "n_test",
]


def evaluate_model(
    name: str,
    features: pd.DataFrame,
    target: pd.Series,
    settings: Settings,
    folds: int,
) -> dict[str, Any]:
    """Fit one model and return its held-out and cross-validated metrics."""
    x_train, x_test, y_train, y_test = split(features, target, settings)
    pipeline = build_pipeline(name, settings.seed, settings.n_jobs)

    started = time.perf_counter()
    pipeline.fit(x_train, y_train)
    fit_seconds = time.perf_counter() - started

    estimator = pipeline.named_steps["clf"]
    has_proba = hasattr(estimator, "predict_proba")
    proba = pipeline.predict_proba(x_test) if has_proba else None
    metrics = classification_metrics(
        y_test, pipeline.predict(x_test), proba, labels=settings.class_labels
    )

    cv = cross_validate_model(
        build_pipeline(name, settings.seed, settings.n_jobs),
        features,
        target,
        folds=folds,
        seed=settings.seed,
        n_jobs=settings.n_jobs,
    )

    return {
        "model": name,
        "status": "ok",
        "accuracy": round(metrics["accuracy"], 4),
        "precision_macro": round(metrics["precision_macro"], 4),
        "recall_macro": round(metrics["recall_macro"], 4),
        "f1_macro": round(metrics["f1_macro"], 4),
        "f1_weighted": round(metrics["f1_weighted"], 4),
        "roc_auc_ovr": (
            round(metrics["roc_auc_ovr"], 4) if "roc_auc_ovr" in metrics else None
        ),
        "cv_mean": round(cv["mean"], 4),
        "cv_std": round(cv["std"], 4),
        "cv_ci_low": round(cv["ci_low"], 4),
        "cv_ci_high": round(cv["ci_high"], 4),
        "fit_seconds": round(fit_seconds, 3),
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
    }


def run_benchmark(
    models: Sequence[str] | None = None,
    settings: Settings | None = None,
    folds: int | None = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """Run the matrix and return a results table sorted by CV macro-F1."""
    settings = settings or get_settings()
    folds = folds or settings.cv_folds
    names = list(models) if models else model_catalog()

    frame = load_source(settings=settings)[0]
    features, target = features_and_target(frame, settings)

    rows: list[dict[str, Any]] = []
    for name in names:
        try:
            row = evaluate_model(name, features, target, settings, folds)
        except Exception as exc:  # noqa: BLE001 - report, do not abort the matrix
            row = {
                "model": name,
                "status": f"error: {exc}",
                "cv_mean": float("nan"),
            }
        rows.append(row)
        if verbose:
            if row.get("status") == "ok":
                print(
                    f"  {name:26s} accuracy={row['accuracy']:.4f} "
                    f"macro_f1={row['f1_macro']:.4f} "
                    f"cv={row['cv_mean']:.4f}±{row['cv_std']:.4f}"
                )
            else:
                print(f"  {name:26s} {row['status']}")

    results = pd.DataFrame(rows)
    for column in METRIC_COLUMNS:
        if column not in results:
            results[column] = None
    return results.sort_values("cv_mean", ascending=False, ignore_index=True)


def to_markdown(results: pd.DataFrame, folds: int) -> str:
    """Render the results table as Markdown for the paper."""
    lines = [
        f"Stratified {folds}-fold cross-validation and a held-out 80/20 split "
        f"on the xAPI Educational Mining Dataset (n=480).",
        "",
        "| Model | Accuracy | Macro F1 | CV macro F1 | CV std | CV 95% CI "
        "| ROC-AUC | Fit s |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in results.iterrows():
        roc = "—" if pd.isna(row.get("roc_auc_ovr")) else f"{row['roc_auc_ovr']:.4f}"
        if row.get("status") != "ok":
            lines.append(
                f"| {row['model']} | — | — | — | — | — | — | {row['status']} |"
            )
            continue
        ci_low = row.get("cv_ci_low")
        ci_high = row.get("cv_ci_high")
        ci = (
            "—"
            if pd.isna(ci_low) or pd.isna(ci_high)
            else f"{ci_low:.3f}–{ci_high:.3f}"
        )
        lines.append(
            f"| {row['model']} | {row['accuracy']:.4f} | {row['f1_macro']:.4f} | "
            f"{row['cv_mean']:.4f} | {row['cv_std']:.4f} | {ci} | "
            f"{roc} | {row['fit_seconds']:.2f} |"
        )
    low, high = BENCHMARK_ACCURACY
    lines += [
        "",
        f"Published ensemble benchmark for this dataset: {low:.2f}–{high:.2f} accuracy "
        "(Amrieh et al., 2016).",
        "",
    ]
    return "\n".join(lines)


def write_figure(results: pd.DataFrame, path: Path) -> None:
    """Write a horizontal comparison chart of CV macro-F1."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ok = results[results["status"] == "ok"].dropna(subset=["cv_mean"])
    ok = ok.sort_values("cv_mean")
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, max(4, 0.42 * len(ok) + 1)))
    ax.barh(
        ok["model"],
        ok["cv_mean"],
        xerr=ok["cv_std"],
        color="#4472C4",
        edgecolor="black",
        linewidth=0.6,
        capsize=3,
    )
    ax.axvline(BENCHMARK_ACCURACY[0], color="#ED7D31", linestyle="--", linewidth=1)
    ax.text(BENCHMARK_ACCURACY[0], -0.8, "benchmark 0.75", color="#ED7D31", fontsize=8)
    ax.set_xlabel("CV macro F1 (10-fold)")
    ax.set_title("SEB-XRIF model comparison matrix")
    ax.set_xlim(0, 1.0)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_reports(
    results: pd.DataFrame,
    out_dir: Path,
    folds: int,
    make_figure: bool = True,
) -> dict[str, Path]:
    """Write CSV, Markdown, and the figure; return the paths written."""
    out_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    csv_path = out_dir / "results.csv"
    results.to_csv(csv_path, index=False)
    written["csv"] = csv_path

    md_path = out_dir / "results.md"
    md_path.write_text(to_markdown(results, folds), encoding="utf-8")
    written["markdown"] = md_path

    json_path = out_dir / "results.json"
    json_path.write_text(
        results.to_json(orient="records", indent=2) + "\n", encoding="utf-8"
    )
    written["json"] = json_path

    if make_figure:
        fig_path = out_dir / "figures" / "model_comparison.png"
        write_figure(results, fig_path)
        written["figure"] = fig_path

    return written


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the SEB-XRIF model matrix.")
    parser.add_argument("--models", nargs="*", default=None, help="Model names.")
    parser.add_argument("--all", action="store_true", help="Run every catalog model.")
    parser.add_argument("--list", action="store_true", help="List catalog models.")
    parser.add_argument("--cv", type=int, default=None, help="Number of CV folds.")
    parser.add_argument("--out", type=Path, default=None, help="Reports output dir.")
    parser.add_argument("--no-figure", action="store_true", help="Skip the figure.")
    args = parser.parse_args(argv)

    if args.list:
        print("Available models:", ", ".join(model_catalog()))
        return

    settings = get_settings()
    folds = args.cv or settings.cv_folds
    names = None if (args.all or not args.models) else args.models

    print(f"Running matrix ({folds}-fold CV) ...")
    results = run_benchmark(models=names, settings=settings, folds=folds)
    out_dir = args.out or settings.reports_dir
    written = write_reports(results, out_dir, folds, make_figure=not args.no_figure)

    best = results.iloc[0]
    print(f"\nBest by CV macro F1: {best['model']} ({best['cv_mean']:.4f})")
    for kind, path in written.items():
        print(f"  {kind}: {path}")


if __name__ == "__main__":
    main()
