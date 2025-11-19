"""Modeling nodes: baseline, AutoML-light oraz model custom."""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

Metrics = Dict[str, float]


# =============================================================================
# Funkcje pomocnicze
# =============================================================================
def _split_features_target(
    data: pd.DataFrame,
    target_column: str,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Dzieli dane na X (cechy numeryczne) i y (target)."""
    X = data.drop(columns=[target_column]).select_dtypes(include=[np.number])
    y = data[target_column]
    return X, y


def _compute_classification_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_proba: np.ndarray | None = None,
) -> Metrics:
    """Liczy podstawowe metryki klasyfikacji binarnej."""
    metrics: Metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
    }

    metrics["roc_auc"] = (
        float(roc_auc_score(y_true, y_proba))
        if y_proba is not None
        else float("nan")
    )

    return metrics


# =============================================================================
# 1. MODEL BAZOWY (Baseline)
# =============================================================================
def train_baseline(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    target_column: str,
) -> Tuple[DummyClassifier, Metrics]:
    """Trenuje DummyClassifier jako baseline oraz liczy metryki."""
    X_train, y_train = _split_features_target(train_data, target_column)
    X_val, y_val = _split_features_target(val_data, target_column)

    model = DummyClassifier(strategy="most_frequent", random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = _compute_classification_metrics(y_val, y_pred, y_proba)
    return model, metrics


# =============================================================================
# 2. AUTOML-LIGHT (sklearn)
# =============================================================================
def train_automl(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    target_column: str,
) -> Tuple[object, Metrics, pd.DataFrame]:
    """
    AutoML-light:
    Testuje kilka modeli (LogReg, RandomForest, GradientBoosting)
    i wybiera najlepszy model po F1-score.
    """
    X_train, y_train = _split_features_target(train_data, target_column)
    X_val, y_val = _split_features_target(val_data, target_column)

    candidates = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000, n_jobs=-1
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=300,
            max_depth=8,
            min_samples_split=4,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "GradientBoosting": GradientBoostingClassifier(
            random_state=42
        ),
    }

    leaderboard_rows = []
    best_model = None
    best_metrics = None
    best_f1 = -1.0

    for name, model in candidates.items():
        model.fit(X_train, y_train)

        y_pred = model.predict(X_val)
        y_proba = model.predict_proba(X_val)[:, 1] if hasattr(model, "predict_proba") else None

        metrics = _compute_classification_metrics(y_val, y_pred, y_proba)

        leaderboard_rows.append({"model": name, **metrics})

        if metrics["f1"] > best_f1:
            best_model = model
            best_metrics = metrics
            best_f1 = metrics["f1"]

    leaderboard_df = pd.DataFrame(leaderboard_rows).sort_values(
        by="f1", ascending=False
    ).reset_index(drop=True)

    return best_model, best_metrics, leaderboard_df


# =============================================================================
# 3. MODEL CUSTOM (RandomForest)
# =============================================================================
def train_custom(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    target_column: str,
) -> Tuple[RandomForestClassifier, Metrics]:
    """Trenuje ręcznie skonfigurowany RandomForest i liczy metryki."""
    X_train, y_train = _split_features_target(train_data, target_column)
    X_val, y_val = _split_features_target(val_data, target_column)

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]

    metrics = _compute_classification_metrics(y_val, y_pred, y_proba)
    return model, metrics


# =============================================================================
# 4. PORÓWNANIE MODELI
# =============================================================================
def evaluate_models(
    baseline_metrics: Metrics,
    automl_metrics: Metrics,
    custom_metrics: Metrics,
) -> dict[str, dict[str, float] | str]:
    """Porównuje metryki trzech modeli i wybiera najlepszy wg F1-score."""
    comparison = {
        "baseline": baseline_metrics,
        "automl": automl_metrics,
        "custom": custom_metrics,
    }

    f1_scores = {name: m["f1"] for name, m in comparison.items()}
    best_model_name = max(f1_scores, key=f1_scores.get)

    return {
        "models": comparison,
        "f1_scores": f1_scores,
        "best_model_by_f1": best_model_name,
    }
