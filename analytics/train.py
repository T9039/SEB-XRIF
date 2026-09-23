"""Training entrypoint.

Trains one or more models from the comparison matrix, evaluates the proposed
Random Forest, and persists the promoted artifact plus metadata, metrics, and
explanation payloads. MLflow logging is best effort so training works without a
running tracking server.

Examples:
    uv run python -m analytics.train
    uv run python -m analytics.train --models random_forest svc knn
    uv run python -m analytics.train --all --tune
"""

from __future__ import annotations

import argparse
import inspect
import json
import platform
import subprocess
from datetime import UTC, datetime
from typing import Any

import joblib
from sklearn import __version__ as sklearn_version

from .config import Settings, get_settings
from .data import class_distribution, features_and_target, load_source, split
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
    name: str, settings: Settings | None = None, *, with_tuning: bool = False
) -> dict[str, Any]:
    """Train one model and return its pipeline and held-out metrics."""
    settings = settings or get_settings()
    df = load_source(settings=settings)[0]
    features, target = features_and_target(df, settings)
    x_train, x_test, y_train, y_test = split(features, target, settings)

    if with_tuning:
        tune(name, x_train, y_train, seed=settings.seed, n_jobs=settings.n_jobs)

    pipeline = build_pipeline(name, settings.seed, settings.n_jobs)
    pipeline.fit(x_train, y_train)

    estimator = pipeline.named_steps["clf"]
    proba = (
        pipeline.predict_proba(x_test) if hasattr(estimator, "predict_proba") else None
    )
    metrics = classification_metrics(
        y_test, pipeline.predict(x_test), proba, labels=settings.class_labels
    )
    metrics["cv"] = cross_validate_model(
        build_pipeline(name, settings.seed, settings.n_jobs),
        features,
        target,
        folds=settings.cv_folds,
        seed=settings.seed,
        n_jobs=settings.n_jobs,
    )
    return {
        "model": name,
        "pipeline": pipeline,
        "metrics": metrics,
        "n_train": int(len(x_train)),
        "n_test": int(len(x_test)),
        "class_distribution": class_distribution(target),
        "features": list(features.columns),
    }


def save_artifact(result: dict[str, Any], settings: Settings) -> dict[str, Any]:
    """Persist the promoted pipeline and its metadata sidecar."""
    settings.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(result["pipeline"], settings.model_path)

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
        "model_version": f"{result['model']}-{_git_commit()}",
        "seed": settings.seed,
        "test_size": settings.test_size,
        "cv_folds": settings.cv_folds,
        "target": settings.target,
        "class_labels": settings.class_labels,
        "feature_order": result["features"],
        "n_train": result["n_train"],
        "n_test": result["n_test"],
        "class_distribution": result["class_distribution"],
        "metrics": result["metrics"],
        "importance": importance,
        "created_utc": datetime.now(UTC).isoformat(),
        "versions": {
            "python": platform.python_version(),
            "scikit_learn": sklearn_version,
        },
        "git_commit": _git_commit(),
    }
    settings.metadata_path.parent.mkdir(parents=True, exist_ok=True)
    settings.metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def _log_mlflow(
    result: dict[str, Any],
    metadata: dict[str, Any],
    settings: Settings,
    *,
    register: bool = True,
    tracking_uri: str | None = None,
    experiment: str | None = None,
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
                    "n_train": str(result["n_train"]),
                    "n_test": str(result["n_test"]),
                }
            )
            mlflow.log_params(
                {
                    "model": result["model"],
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
                    settings.mlflow_registered_model if register else None
                ),
                **log_kwargs,
            )
            return str(run.info.run_id)
    except Exception as exc:  # noqa: BLE001
        print(f"[mlflow] skipped: {exc}")
        return None


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Train SEB-XRIF models.")
    parser.add_argument(
        "--models",
        nargs="*",
        default=["random_forest"],
        help="Model names to train (see --list).",
    )
    parser.add_argument("--all", action="store_true", help="Train the full matrix.")
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
    names = model_catalog() if args.all else args.models

    results: dict[str, dict[str, Any]] = {}
    for name in names:
        print(f"Training {name} ...")
        result = train_model(name, settings, with_tuning=args.tune)
        results[name] = result
        f1 = result["metrics"]["f1_macro"]
        acc = result["metrics"]["accuracy"]
        print(f"  {name}: accuracy={acc:.4f} macro-F1={f1:.4f}")

    # Promote the Random Forest as the dashboard artifact by default.
    promoted = results.get("random_forest") or results[names[0]]
    metadata = save_artifact(promoted, settings)

    shap_data = shap_payload(
        promoted["pipeline"],
        load_source(settings=settings)[0][settings.feature_columns],
    )
    settings.metadata_path.with_name("shap.json").write_text(
        json.dumps(shap_data, indent=2), encoding="utf-8"
    )

    if not args.no_mlflow:
        run_id = _log_mlflow(
            promoted,
            metadata,
            settings,
            register=not args.no_register,
            tracking_uri=args.tracking_uri,
            experiment=args.experiment,
        )
        if run_id:
            print(f"MLflow run -> {run_id}")

    print(f"Promoted '{promoted['model']}' -> {settings.model_path}")
    print(f"Metadata -> {settings.metadata_path}")


if __name__ == "__main__":
    main()
