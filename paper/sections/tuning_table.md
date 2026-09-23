### Tuned configurations

| Model | Best CV macro F1 | Best parameters |
| --- | --- | --- |
| random_forest | 0.7891 | n_estimators=200, max_depth=18, min_samples_split=9, min_samples_leaf=1, max_features=sqrt |
| extra_trees | 0.8002 | n_estimators=300, max_depth=20, min_samples_leaf=1, max_features=log2 |
| xgboost | 0.8001 | n_estimators=200, max_depth=8, learning_rate=0.026295533959661995, subsample=0.6480364465854224, colsample_bytree=0.6537753224463684, reg_lambda=0.8695071323994635 |
| lightgbm | 0.7872 | n_estimators=400, num_leaves=35, learning_rate=0.023132701179483704, min_child_samples=38, colsample_bytree=0.7300570135729483 |
| catboost | 0.8089 | iterations=200, depth=6, learning_rate=0.04345454109729477, l2_leaf_reg=0.07476312062252301 |
