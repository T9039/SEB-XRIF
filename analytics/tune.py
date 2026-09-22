"""Hyperparameter tuning.

Optuna (TPE with median pruning) is the default search strategy. GridSearchCV
is retained for the Random Forest so the configuration quoted in the paper is
exactly reproducible. See specification section 4.6.
"""
from __future__ import annotations


def tune_optuna(model_name: str, n_trials: int = 50, seed: int = 42):
    """Tune a model with Optuna and return the best parameters."""
    raise NotImplementedError("Implemented in build-plan phase 4.")


def tune_grid_random_forest(seed: int = 42):
    """Exhaustive grid search for the Random Forest configuration."""
    raise NotImplementedError("Implemented in build-plan phase 4.")
