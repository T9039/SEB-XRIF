# 5. Developments

This section reports what was built. SEB-XRIF is implemented as four cooperating
layers, each independently testable, and is reproducible from a clean checkout.

## 5.1 Data layer

The bundled records are validated against an explicit schema and versioned with
DVC. The framework then demonstrates the standard path it asks adopters to use:
each learner row is encoded as Experience API statements — a registration
statement carrying the demographics, one statement per behavioural metric, and a
completion statement carrying the outcome — posted to a Learning Record Store
(`lrsql`, running against PostgreSQL), and read back into a feature table that
validates against the same schema as the source. The 480 learners produced 2,880
statements and reconstructed to 480 validated rows.

The analytics database uses SQLAlchemy models for learners, activity events,
predictions, and evaluations, created by Alembic migrations. The API reads
learners from the database when it is populated and falls back to the bundled CSV
otherwise, so the same code runs in development and in deployment.

## 5.2 Analytics layer

A single scikit-learn pipeline applies one-hot encoding to categorical
predictors and passes behavioural counts through unchanged. Sixteen estimators
are trained under an identical stratified split and cross-validation, spanning
classical, tree, boosting, kernel, instance-based, neural, and ensemble families.
Hyperparameters are tuned with Optuna, and the Random Forest (100 trees, balanced
class weights, fixed seed) is promoted as the framework default. Interpretability
combines native importance, cross-fold permutation importance, and SHAP.

## 5.3 Service layer

A FastAPI service exposes single and batch prediction, model metrics, feature
importance, behavioural trends, a paged learner table, categorical option sets,
health, and version endpoints. It loads the model once at startup, from a local
artifact or the MLflow model registry, validates every request, emits structured
logs with request identifiers, and returns a consistent error envelope.

## 5.4 Visualization layer

The dashboard is a React application built with Vite+ on a shared shadcn/ui
component library that also drives its own Storybook. Reflecting the layers
above, it is organised into a side panel with four sections: Overview, Predict,
Data, and Diagnostics. The Predict section posts the sixteen predictors to the
service and returns the tier with per-class probabilities; the Diagnostics
section reports the confusion matrix and cross-validation spread.

## 5.5 Reproducibility and tooling

Data, models, and metrics are reproducible: DVC pins the data and pipeline,
MLflow records every run and registers the model, and seeds are fixed
throughout. The project ships as a pnpm workspace for the web and UI packages,
uses `uv` for Python, and brings the database, LRS, MLflow, service, and
dashboard up together with Docker Compose. GitHub Actions runs the full test
suite, type and lint checks, image builds, and the paper build on every change.
