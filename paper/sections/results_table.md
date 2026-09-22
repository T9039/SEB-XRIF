Stratified 10-fold cross-validation and a held-out 80/20 split on the xAPI Educational Mining Dataset (n=480).

| Model | Accuracy | Macro F1 | CV macro F1 | CV std | ROC-AUC | Fit (s) |
| --- | --- | --- | --- | --- | --- | --- |
| random_forest | 0.7604 | 0.7688 | 0.8070 | 0.0493 | 0.9113 | 0.16 |
| stacking | 0.7708 | 0.7766 | 0.8002 | 0.0389 | 0.9197 | 1.86 |
| extra_trees | 0.7812 | 0.7857 | 0.7972 | 0.0535 | 0.9221 | 0.15 |
| catboost | 0.7812 | 0.7895 | 0.7924 | 0.0605 | 0.9022 | 1.41 |
| mlp | 0.7604 | 0.7676 | 0.7904 | 0.0347 | 0.9104 | 0.77 |
| voting | 0.8021 | 0.8074 | 0.7817 | 0.0699 | 0.9042 | 0.24 |
| lightgbm | 0.7500 | 0.7574 | 0.7815 | 0.0464 | 0.8956 | 0.25 |
| xgboost | 0.7292 | 0.7350 | 0.7789 | 0.0593 | 0.8900 | 0.23 |
| gradient_boosting | 0.7708 | 0.7770 | 0.7725 | 0.0552 | 0.8884 | 0.42 |
| hist_gradient_boosting | 0.7708 | 0.7747 | 0.7688 | 0.0513 | 0.8926 | 0.45 |
| svc | 0.7812 | 0.7857 | 0.7650 | 0.0723 | 0.8892 | 0.05 |
| logistic_regression | 0.7500 | 0.7570 | 0.7641 | 0.0787 | 0.8874 | 0.03 |
| decision_tree | 0.6354 | 0.6446 | 0.7460 | 0.0820 | 0.7372 | 0.01 |
| knn | 0.7188 | 0.7276 | 0.7139 | 0.0712 | 0.8646 | 0.01 |
| naive_bayes | 0.6042 | 0.5970 | 0.5591 | 0.0932 | 0.8090 | 0.01 |
| dummy | 0.4375 | 0.2029 | 0.2036 | 0.0020 | 0.5000 | 0.01 |

Published ensemble benchmark for this dataset: 0.75–0.83 accuracy (Amrieh et al., 2016).
