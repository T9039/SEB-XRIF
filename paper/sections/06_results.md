# 6. Results

The comparison matrix trains sixteen estimators on the xAPI Educational Mining
Dataset (n=480) with a held-out 80/20 split and stratified ten-fold
cross-validation. Random Forest is the strongest model by cross-validated macro
F1 (0.807, held-out accuracy 0.760), closely followed by stacking (0.800) and
extra trees (0.797). Every tree and boosting family sits within or above the
published 0.75–0.83 accuracy benchmark for this dataset, while the dummy baseline
(0.204) confirms the task is not trivially learnable. Hyperparameter tuning with
Optuna raised the best models further; CatBoost reached 0.809 under five-fold
tuning. The spread of fold scores is reported alongside the mean, so the result
is not read from a single favourable split.

The table below reports accuracy, macro F1, cross-validated macro F1 with its
standard deviation, one-vs-rest ROC-AUC, and fit time for every model.

Interpretability is consistent across folds: the most stable drivers are
`StudentAbsenceDays` (permutation importance 0.194 ± 0.020), `Relation`,
`VisITedResources`, and `raisedhands`. These are plausible, actionable signals —
attendance and resource engagement — which supports the framework's use of the
model for early support rather than for gatekeeping.

The evaluation protocol is fixed and reported with the same instruments for
every adopter: System Usability Scale for the dashboard and Cohen's d for the
learning effect, with T0 (baseline), T1 (immediate), and T2 (one semester later)
time points. In the illustrative pilot report the dashboard meets the usability
benchmark (mean SUS 82.5 against 76.6) and the immediate learning effect exceeds
the reference (d well above 0.936), while the delayed measurement is reported as
scheduled and not yet due.

The full comparison matrix is printed below, and the corresponding chart is shown
in the figure.
