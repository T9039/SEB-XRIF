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
standard deviation and 95 percent confidence interval, one-vs-rest ROC-AUC, and
fit time for every model.

Interpretability is consistent across folds: the most stable drivers are
`StudentAbsenceDays` (permutation importance 0.194 ± 0.020), `Relation`,
`VisITedResources`, and `raisedhands`. These are plausible, actionable signals —
attendance and resource engagement — which supports the framework's use of the
model for early support rather than for gatekeeping.

The XR transfer is demonstrated on the five ARETE augmented-reality exports. The
same pipeline parses each, normalises delimiter, columns, encodings, and result
shape, reconstructs per-learner engagement, plots engagement over time, and
predicts a later drop-off from early-session behaviour. Cross-validated ROC-AUC
is 0.69 for PBIS, 0.88 for English Literacy and STEM Geometry, and 0.73 for STEM
Geography; the LXD pilot is a single-outcome cohort and is reported as not
modelled. These early-warning results on real XR xAPI data show the schema
transfer works; they are not a claim about XR learning outcomes.

The evaluation protocol is fixed and reported with the same instruments for
every adopter: System Usability Scale for the dashboard and Cohen's d for the
learning effect, over T0 (baseline), T1 (immediate), and T2 (one semester later).
The store is empty until the DUT pilot runs, and the evaluation endpoint returns
an explicit "no pilot data yet" state. The bundled `eval/pilot.example.json` is
tagged as example provenance and is not presented as a result.

The full comparison matrix is printed below, and the corresponding chart is shown
in the figure.
