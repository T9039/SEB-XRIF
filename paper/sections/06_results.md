# 6. Results

The comparison matrix trains sixteen estimators on the xAPI Educational Mining Dataset
(n=480) with a held-out 80/20 split and stratified ten-fold cross-validation. Random Forest
is the strongest model by cross-validated macro F1 (0.807), closely followed by stacking
and extra trees. All tree-based and boosting families cluster within or above the published
0.75–0.83 accuracy benchmark for this dataset, while the dummy baseline confirms the task
is not trivially learnable.

The table below reports accuracy, macro F1, cross-validated macro F1 with its standard
deviation, one-vs-rest ROC-AUC, and fit time for every model.
