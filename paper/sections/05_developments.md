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

The same data contract ingests the public ARETE augmented-reality pilots. Their
Learning Locker exports differ in delimiter, column names, encodings, and result
shape; the adapter normalises all of it, maps raw verbs onto stable behaviour
classes, and reconstructs per-learner engagement features validated against the
XR schema.

## 5.2 Analytics layer

A single scikit-learn pipeline applies one-hot encoding to categorical
predictors and passes behavioural counts through unchanged. Sixteen estimators
are trained under an identical stratified split and cross-validation, spanning
classical, tree, boosting, kernel, instance-based, neural, and ensemble families.
Hyperparameters are tuned with Optuna, and the Random Forest (100 trees, balanced
class weights, fixed seed) is promoted as the framework default. Interpretability
combines native importance, cross-fold permutation importance, and SHAP.

The class labels are reported as support bands, and a cost-sensitive rule can
flag the priority band below the argmax. The comparison matrix reports 95 percent
confidence intervals, diagnostics report calibration (reliability, Brier, and
expected calibration error), and a second model predicts XR engagement drop-off
from early-session behaviour with cross-validated ROC-AUC. Training is
dataset-driven: any registered source — the LMS seed, an ARETE pilot, or an
uploaded dataset — declares its own features and target, and is trained and
promoted either with a chosen algorithm or by running the matrix and promoting
the best model for that data.

## 5.3 Service layer

A FastAPI service exposes single and batch prediction, model metrics, feature
importance, behavioural trends, the learner table, the comparison matrix,
diagnostics, Chart Studio queries, the ARETE pilots, XR trends and risk, and a
longitudinal evaluation summary. It loads the model once at startup, from a local
artifact or the MLflow model registry, validates every request, emits structured
logs with request identifiers, and returns a consistent error envelope.

## 5.4 Visualization layer

The dashboard is a React application built with Vite+ on a shared shadcn/ui
component library that also drives its own Storybook. It has seven tabs —
Overview, Predict, Data, Diagnostics, Explore, Studio, and Datasets — and a
persistent header selector that switches the active data source between the LMS
seed and the five ARETE XR pilots, with a light/dark theme toggle. Predict returns
the support band with per-class probabilities; Diagnostics reports the confusion
matrix, calibration, and cross-validation spread; Explore shows the ARETE
engagement trends, XR early-warning risk, and the LMS-to-XR feature mapping;
Overview shows the longitudinal impact panel, empty until pilot data is imported.
The Datasets tab checks an upload against the profile, lets a plain table be
adapted with a column mapping, flattens a foreign xAPI file to a mappable table,
and trains the resulting source.

## 5.5 Reproducibility and tooling

Data, models, and metrics are reproducible: DVC pins the data and pipeline,
MLflow records every run and registers the model, and seeds are fixed
throughout. A clean-checkout check re-runs the pipeline and fails if the recorded
graph drifts, and the generated model metadata is deterministic so it can be
verified. The project ships as a pnpm workspace for the web and UI packages,
uses `uv` for Python, and brings the database, LRS, MLflow, service, and
dashboard up together with Docker Compose; a single command installs what is
missing, trains the default model if absent, and starts the service and
dashboard. GitHub Actions runs the full test suite, type and lint checks, image
builds, the reproduction check, and the paper build on every change.

The service was exercised end-to-end as a user would, through the browser, with
both conformant and malformed inputs: missing or extra prediction features,
unknown sources, oversized uploads, non-UTF-8 files, tables with no target, and
foreign xAPI vocabularies. Failures are reported as structured, actionable
errors, and a source whose training fails is rolled back rather than left
half-registered.
