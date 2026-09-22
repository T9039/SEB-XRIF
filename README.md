# SEB-XRIF

**Scalable, Evidence-Based XR Integration Framework** — a reusable, reproducible
way of conducting XR education research. This repository holds the data,
analytics, service, visualization, and evaluation layers of the framework.

Team 3 · PRJT302 · Information Technology, Durban University of Technology.

## What this is

SEB-XRIF is not a single model or dashboard. It is a standard recipe: any
institution exports learning data in the xAPI schema, runs the same analytics
pipeline with the same seed and configuration, and reports the same evaluation
metrics. The Random Forest and the dashboard are the first instantiation of the
framework, not the framework itself.

The four layers:

| Layer | Purpose | Status |
| --- | --- | --- |
| Data | xAPI-schema learning data, validated and versioned | Phase 1 |
| Analytics | Predict Low/Medium/High tier from logged behaviour; rank drivers | Phase 3–6 |
| Service | FastAPI prediction and metrics endpoints | Phase 7 |
| Visualization | Dashboard over the API (placeholder UI) | Phase 8 |
| Evaluation | Accuracy/F1/CV, SUS, Cohen's d, T0/T1/T2 protocol | Phase 9 |

## Status

Phase 0 — scaffold. The full specification and phased build plan live in
[`docs/SEB-XRIF_Technical_Specification.pdf`](docs/SEB-XRIF_Technical_Specification.pdf)
(source: `docs/SEB-XRIF_Technical_Specification.typ`).

## Quickstart

Requires [`uv`](https://docs.astral.sh/uv/) and Python 3.12 (managed by `uv`).

```bash
uv sync                 # create the environment and install dependencies
uv run pytest           # run the test suite
uv run uvicorn api.main:app --reload   # start the API
```

## Repository layout

```
data/       raw and processed datasets (DVC-tracked)
analytics/  schema, preprocessing, training, tuning, evaluation, explanations
models/     serialized pipelines and metadata sidecars
api/        FastAPI service and Pydantic schemas
web/        React + Vite dashboard (placeholder UI)
eval/       SUS, effect sizes, longitudinal T0/T1/T2 protocol
docs/       technical specification, paper tooling, generated figures
tests/      Python tests
notebooks/  exploratory analysis
```

## Stack

- **Data:** pandas, pandera, SQLAlchemy, DVC
- **Analytics:** scikit-learn, XGBoost, LightGBM, CatBoost, Optuna, SHAP
- **Tracking:** MLflow, DVC
- **Service:** FastAPI, Pydantic, uvicorn, gunicorn
- **Frontend:** React, Vite, TypeScript, Chart.js, TanStack Query
- **Evaluation:** scikit-learn metrics, pingouin, scipy (see GPL-3 note in spec)

Full rationale, alternatives, and version pins are in the technical
specification, Appendices A and B.

## Data

`data/raw/xAPI-Edu-Data.csv` — the xAPI Educational Mining Dataset (Kalboard
360), 480 records, CC BY-SA 4.0. See the specification for provenance.

## License

Code is released under the MIT License (see [`LICENSE`](LICENSE)). The bundled
dataset retains its CC BY-SA 4.0 license.
