# 5. Developments

This section reports how the analytics pipeline was actually implemented. It is completed
in T20, drawing directly from `reports/` and the MLflow runs so the numbers cannot drift
from the code.

## 5.1 Data engineering

The raw xAPI Educational Mining Dataset is validated against a schema, versioned with DVC,
and ingested into the framework. The implementation adds a real Experience API path: the
records are represented as xAPI statements and loaded into a Learning Record Store, then
read back into the analytics layer.

## 5.2 Analytics and the comparison matrix

A single scikit-learn pipeline performs one-hot encoding, a stratified split, and model
fitting. The full comparison matrix spans sixteen estimators across classical, tree,
boosting, kernel, instance-based, neural, and ensemble families, each evaluated with
stratified ten-fold cross-validation.

## 5.3 Service and dashboard

The promoted pipeline is served through a FastAPI service exposing prediction, metrics,
importance, and trend endpoints, and a React dashboard built on a shared component library
visualises tiers, behaviour, and feature importance.

**TODO (T20):** replace the outline above with the implementation narrative, configuration,
and reproducibility description.
