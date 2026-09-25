# Reproducibility

SEB-XRIF's core claim is that any institution can export xAPI data, run the
same pipeline with the same configuration, and obtain a comparable result.
This page describes how that is pinned and how to verify it.

## What is pinned

- **Environment** — `uv.lock` (Python 3.12) and `pnpm-lock.yaml` fix every
  dependency version.
- **Configuration** — `analytics/config.yaml` fixes the seed, the test split,
  the cross-validation folds, the feature columns, and the target.
- **Data and artifacts** — DVC records the raw dataset, the processed parquet,
  the promoted model, and the metadata sidecar in `dvc.lock`.
- **Runs** — MLflow records each training run; seeds and a single-threaded
  default keep results stable.

## Reproduce from a clean checkout

```bash
git clone git@github.com:T9039/SEB-XRIF.git
cd SEB-XRIF
uv sync
uv run dvc repro        # rebuilds data/processed and models/ from the raw CSV
```

`dvc repro` runs the two declared stages (`prepare`, then `train`) and writes
`data/processed/learners.parquet`, `models/model.joblib`, `models/shap.json`,
and `models/model.meta.json`. `dvc status` should report "Data and pipelines
are up to date".

## Verify it still reproduces

```bash
make repro-check
```

The check copies the tracked tree into a temporary directory with no DVC
cache, re-runs the pipeline there, and fails if the regenerated `dvc.lock`
differs from the committed one. A difference means the recorded artifacts no
longer match the sources that are supposed to produce them. CI runs the same
check on every push and pull request.

## Deterministic metadata vs run provenance

`models/model.meta.json` is part of the reproducible graph, so it must be
byte-for-byte stable. It therefore contains only deterministic fields
(metrics, feature order, class distribution, library versions) and is written
with sorted keys.

Volatile provenance — the training timestamp, the git commit, and the
`{model}-{commit}` version string — is written to a separate
`models/model.run.json`. DVC does not track that file; the API merges it over
the deterministic metadata at load time, so `/version` and `/health` still
report the commit that produced the artifact.

## Running on your own xAPI data

The pipeline reads the bundled dataset by default. To reproduce on your own
export, either place it at `data/raw/xAPI-Edu-Data.csv` (matching the schema in
`analytics/schema.py`) or point `analytics/config.yaml` at it, then run the
same `uv run dvc repro`. The fixed evaluation protocol (see `eval/README.md`)
is what makes results comparable across institutions.
