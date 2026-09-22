# Analytics layer

Predicts a Low/Medium/High performance tier from logged learning behaviour and
ranks the behaviours that drive the prediction. This is the framework's
analytics layer; the Random Forest is its first instantiation.

## Modules

| Module | Responsibility |
| --- | --- |
| `config.py` | Loads `config.yaml` into a frozen `Settings` object |
| `schema.py` | pandera schema for the 16 predictors and the target |
| `data.py` | CSV load, validation, feature/target split, stratified split |
| `preprocess.py` | Tree and scaled `ColumnTransformer` builders |
| `models.py` | Full comparison-matrix catalog and pipeline factory |
| `train.py` | Training runner, artifact + metadata + SHAP export, MLflow logging |
| `tune.py` | Optuna tuning and a Random Forest grid search |
| `evaluate.py` | Metrics and stratified 10-fold cross-validation |
| `explain.py` | Native, permutation, and SHAP importance payloads |

## Commands

```bash
make prepare                                  # validate + write parquet
make train                                    # Random Forest (proposed)
make train ARGS='--all'                       # full comparison matrix
make train ARGS='--models svc knn xgboost'    # selected models
make train ARGS='--tune'                      # tune before fitting
uv run python -m analytics.train --list       # list models
```

## Model catalog

`uv run python -m analytics.train --list` prints the live catalog. Current
entries: `dummy`, `logistic_regression`, `decision_tree`, `naive_bayes`,
`random_forest`, `extra_trees`, `gradient_boosting`,
`hist_gradient_boosting`, `svc`, `knn`, `xgboost`, `lightgbm`, `catboost`,
`voting`, `stacking`, `mlp`.

## Configuration

Edit `config.yaml`. Every path is resolved relative to the repository root.
The seed, split, and cross-validation folds are fixed for reproducibility; see
the technical specification, section 4.5.

## Artifacts produced by training

- `models/model.joblib` — the promoted scikit-learn pipeline (preprocessing
  included, so serving applies the identical transform)
- `models/model.meta.json` — metrics, feature order, library versions, git
  commit, and class distribution
- `models/shap.json` — global SHAP summary for the dashboard
