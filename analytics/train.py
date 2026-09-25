"""Training entrypoint.

Trains a model (or the full comparison matrix) for a dataset source, promotes
the best model, and persists the artifact, metadata, and SHAP payload for that
source. MLflow logging is best effort so training works without a running
tracking server.

Examples:
    uv run python -m analytics.train
    uv run python -m analytics.train --source arete-pbis --matrix
    uv run python -m analytics.train --source my-upload --models random_forest svc
"""

from __future__ import annotations

import argparse
import inspect
import json
import platform
import subprocess
from dataclasses import replace
from datetime import UTC, datetime
from typing import Any

import joblib
from sklearn import __version__ as sklearn_version

from .config import Settings, get_settings
from .data import class_distribution, load_dataset, split
from .evaluate import classification_metrics, cross_validate_model
from .explain import feature_importance, shap_payload
from .models import build_pipeline, model_catalog
from .tune import tune


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def train_model(
    name: str,
    settings: Settings | None = None,
    *,
    with_tuning: bool = False,
    dataset=None,
) -> dict[str, Any]:
    """Train one model for a dataset and return its pipeline and metrics."""
    settings = settings or get_settings()
    dataset = dataset or load_dataset(settings)
    if not dataset.supervised:
        raise ValueError(f"Dataset '{dataset.name}' has no target to train on.")

    features = dataset.frame[dataset.features]
    target = dataset.frame[dataset.target]
    labels = list(dataset.class_labels) or sorted(
        str(value) for value in target.unique()
    )
    x_train, x_test, y_train, y_test = split(features, target, settings)

    if with_tuning:
        tune(name, x_train, y_train, seed=settings.seed, n_jobs=settings.n_jobs)

    def build() -> Any:
        return build_pipeline(
            name,
            settings.seed,
            settings.n_jobs,
            dataset.categorical,
            dataset.numeric,
        )

    pipeline = build()
    pipeline.fit(x_train, y_train)

    estimator = pipeline.named_steps["clf"]
    proba = (
        pipeline.predict_proba(x_test) if hasattr(estimator, "predict_proba") else None
    )
    metrics = classification_metrics(
        y_test, pipeline.predict(x_test), proba, labels=labels
    )
    metrics["cv"] = cross_validate_model(
        build(),
        features,
        target,
        folds=settings.cv_folds,
        seed=settings.seed,
        n_jobs=settings.n_jobs,
    )
    return {
        "model": name,
        "source": dataset.name,
        "target": dataset.target,
        "class_labels": labels,
        "pipeline": pipeline,
        "metrics": metrics,
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "class_distribution": class_distribution(target),
        "features": list(features.columns),
    }


def save_artifact(
    result: dict[str, Any], settings: Settings, source: str | None = None
) -> dict[str, Any]:
    """Persist the promoted pipeline and its metadata sidecar for a source.

    The metadata sidecar is deterministic so it can be verified by the
    reproducible pipeline (DVC): it must not embed timestamps or the current
    commit. Volatile provenance is written to a separate run sidecar that DVC
    does not track, and the two are returned merged.
    """
    source = source or str(result.get("source") or settings.dataset)
    model_path, metadata_path, run_path = settings.artifacts_for(source)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result["pipeline"], model_path)

    importance: dict[str, Any]
    try:
        importance = {
            "available": True,
            "importance": feature_importance(result["pipeline"]),
        }
    except AttributeError as exc:
        importance = {"available": False, "reason": str(exc)}

    metadata = {
        "model": result["model"],
        "source": source,
        "seed": settings.seed,
        "test_size": settings.test_size,
        "cv_folds": settings.cv_folds,
        "target": result.get("target", settings.target),
        "class_labels": result.get("class_labels", settings.class_labels),
        "feature_order": result["features"],
        "n_train": result["n_train"],
        "n_test": result["n_test"],
        "class_distribution": result["class_distribution"],
        "metrics": result["metrics"],
        "importance": importance,
        "versions": {
            # Record only major.minor: the patch release differs across
            # machines and would otherwise make the reproducible artifact drift.
            "python": ".".join(platform.python_version_tuple()[:2]),
            "scikit_learn": sklearn_version,
        },
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )

    run = {
        "model_version": f"{result['model']}-{_git_commit()}",
        "created_utc": datetime.now(UTC).isoformat(),
        "git_commit": _git_commit(),
    }
    run_path.write_text(json.dumps(run, indent=2, sort_keys=True), encoding="utf-8")
    return {**metadata, **run}


def _log_mlflow(
    result: dict[str, Any],
    metadata: dict[str, Any],
    settings: Settings,
    *,
    register: bool = True,
    tracking_uri: str | None = None,
    experiment: str | None = None,
    registered_model: str | None = None,
) -> str | None:
    """Log the run to MLflow and register the model; best effort.

    Returns the MLflow run id when logging succeeds, otherwise ``None``.
    """
    try:
        import mlflow
        import mlflow.sklearn

        mlflow.set_tracking_uri(tracking_uri or settings.tracking_uri())
        mlflow.set_experiment(experiment or settings.mlflow_experiment)
        with mlflow.start_run(run_name=result["model"]) as run:
            mlflow.set_tags(
                {
                    "git_commit": str(metadata.get("git_commit")),
                    "model_version": str(metadata.get("model_version")),
                    "source": str(metadata.get("source")),
                    "n_train": str(result["n_train"]),
                    "n_test": str(result["n_test"]),
                }
            )
            mlflow.log_params(
                {
                    "model": result["model"],
                    "source": str(metadata.get("source")),
                    "seed": settings.seed,
                    "test_size": settings.test_size,
                    "cv_folds": settings.cv_folds,
                }
            )
            mlflow.log_metrics(
                {
                    key: value
                    for key, value in result["metrics"].items()
                    if isinstance(value, (int, float))
                }
            )
            mlflow.log_dict(metadata, "metadata.json")
            log_kwargs: dict[str, Any] = {}
            if (
                "skops_trusted_types"
                in inspect.signature(mlflow.sklearn.log_model).parameters
            ):
                # MLflow 3 serialises with skops and requires explicit trust
                # for scikit-learn internals such as the tree node store.
                log_kwargs["skops_trusted_types"] = ["sklearn.tree._tree.Tree"]
            mlflow.sklearn.log_model(
                result["pipeline"],
                name="model",
                registered_model_name=(
                    (registered_model or settings.mlflow_registered_model)
                    if register
                    else None
                ),
                **log_kwargs,
            )
            return str(run.info.run_id)
    except Exception as exc:  # noqa: BLE001
        print(f"[mlflow] skipped: {exc}")
        return None


def train_source(
    source: str,
    settings: Settings | None = None,
    *,
    models: list[str] | None = None,
    matrix: bool = False,
    with_tuning: bool = False,
    no_mlflow: bool = False,
    register: bool = True,
    tracking_uri: str | None = None,
    experiment: str | None = None,
) -> dict[str, Any]:
    """Train and promote a model for one source (single model or best-of-matrix)."""
    settings = settings or get_settings()
    if source != settings.dataset:
        settings = replace(settings, dataset=source)
    dataset = load_dataset(settings)

    names = model_catalog() if matrix else (models or ["random_forest"])
    results: dict[str, dict[str, Any]] = {}
    for name in names:
        print(f"Training {name} on {dataset.name} ...")
        result = train_model(name, settings, with_tuning=with_tuning, dataset=dataset)
        results[name] = result
        f1 = result["metrics"]["f1_macro"]
        acc = result["metrics"]["accuracy"]
        print(f"  {name}: accuracy={acc:.4f} macro-F1={f1:.4f}")

    if matrix:
        promoted = max(results.values(), key=lambda row: row["metrics"]["cv"]["mean"])
    else:
        promoted = results.get("random_forest") or max(
            results.values(), key=lambda row: row["metrics"]["cv"]["mean"]
        )

    metadata = save_artifact(promoted, settings, source=source)
    shap_path = settings.shap_for(source)
    shap_data = shap_payload(promoted["pipeline"], dataset.frame[dataset.features])
    shap_path.parent.mkdir(parents=True, exist_ok=True)
    shap_path.write_text(json.dumps(shap_data, indent=2), encoding="utf-8")

    if not no_mlflow:
        registered = (
            settings.mlflow_registered_model
            if source == "kalboard"
            else f"seb-xrif-{source}"
        )
        run_id = _log_mlflow(
            promoted,
            metadata,
            settings,
            register=register,
            tracking_uri=tracking_uri,
            experiment=experiment,
            registered_model=registered,
        )
        if run_id:
            print(f"MLflow run -> {run_id}")

    model_path, metadata_path, _ = settings.artifacts_for(source)
    print(f"Promoted '{promoted['model']}' -> {model_path}")
    print(f"Metadata -> {metadata_path}")
    return promoted


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train SEB-XRIF models.")
    parser.add_argument(
        "--source",
        default=None,
        help="Dataset source to train (see: list_sources). Defaults to the config.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        default=["random_forest"],
        help="Model names to train (see --list).",
    )
    parser.add_argument(
        "--matrix",
        "--all",
        dest="matrix",
        action="store_true",
        help="Train the full matrix and promote the best model.",
    )
    parser.add_argument("--tune", action="store_true", help="Tune before fitting.")
    parser.add_argument("--list", action="store_true", help="List available models.")
    parser.add_argument("--no-mlflow", action="store_true", help="Skip MLflow logging.")
    parser.add_argument("--tracking-uri", default=None, help="MLflow tracking URI.")
    parser.add_argument("--experiment", default=None, help="MLflow experiment name.")
    parser.add_argument(
        "--no-register",
        action="store_true",
        help="Log the run but do not register the model.",
    )
    args = parser.parse_args(argv)

    if args.list:
        print("Available models:", ", ".join(model_catalog()))
        return

    settings = get_settings()
    source = args.source or settings.dataset
    train_source(
        source,
        settings,
        models=args.models,
        matrix=args.matrix,
        with_tuning=args.tune,
        no_mlflow=args.no_mlflow,
        register=not args.no_register,
        tracking_uri=args.tracking_uri,
        experiment=args.experiment,
    )


if __name__ == "__main__":
    main()
