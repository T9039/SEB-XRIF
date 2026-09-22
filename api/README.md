# Service layer

FastAPI service that loads the promoted pipeline once at startup and exposes
prediction and analytics endpoints. It starts even without a trained model:
prediction and metrics routes return HTTP 503 until one exists.

## Run

```bash
make api                 # http://localhost:8000
make dev                 # api + dashboard together
PORT=9000 ./scripts/run-api.sh
```

Interactive docs are served at `/docs`.

## Configuration

Settings are read from the environment with the `SEBXRIF_` prefix, or a `.env`
file. Defaults point at the repository layout.

| Variable | Default | Purpose |
| --- | --- | --- |
| `SEBXRIF_MODEL_PATH` | `models/model.joblib` | Promoted pipeline |
| `SEBXRIF_METADATA_PATH` | `models/model.meta.json` | Metrics and metadata |
| `SEBXRIF_SHAP_PATH` | `models/shap.json` | SHAP payload |
| `SEBXRIF_RAW_DATA_PATH` | `data/raw/xAPI-Edu-Data.csv` | Trends source |
| `SEBXRIF_TARGET` | `Class` | Target column |
| `MLFLOW_TRACKING_URI` | `file:./mlruns` | MLflow (training) |

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Banner and endpoint list |
| `GET` | `/health` | Liveness and model-loaded status |
| `POST` | `/predict` | Single-learner tier prediction |
| `POST` | `/predict/batch` | Vectorized prediction |
| `GET` | `/metrics` | Active model metrics |
| `GET` | `/importance` | Native + SHAP importance |
| `GET` | `/trends` | Class counts and behaviour by tier |

## Example

```bash
curl -s localhost:8000/health | jq
curl -s localhost:8000/trends | jq '.class_counts'

curl -s localhost:8000/predict -H 'Content-Type: application/json' -d '{
  "gender":"M","NationalITy":"KW","PlaceofBirth":"KuwaIT",
  "StageID":"lowerlevel","GradeID":"G-04","SectionID":"A","Topic":"IT",
  "Semester":"F","Relation":"Father","ParentAnsweringSurvey":"Yes",
  "ParentschoolSatisfaction":"Good","StudentAbsenceDays":"Under-7",
  "raisedhands":15,"VisITedResources":16,"AnnouncementsView":2,"Discussion":20
}' | jq
```

## Design notes

- The model is loaded once at startup (never per request).
- Input is validated by Pydantic before it reaches the model.
- The input vector is rebuilt in the metadata's `feature_order`, so column
  reordering cannot silently corrupt predictions.
- In production the container runs `gunicorn` with `uvicorn` workers.
