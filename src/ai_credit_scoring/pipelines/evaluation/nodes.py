
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import cross_val_score

Metrics = Dict[str, float]


# =============================================================================
# Cross-validation
# =============================================================================
def cross_validate_model(
    model: Any,
    train_data: pd.DataFrame,
    target_column: str,
    cv_folds: int = 5,
    cv_scoring: str = "f1",
    random_state: int = 42,
) -> Dict[str, Any]:

    X = train_data.drop(columns=[target_column]).select_dtypes(include=[np.number])
    y = train_data[target_column]
    
    cv_scores = cross_val_score(
        model, X, y, cv=cv_folds, scoring=cv_scoring, n_jobs=-1
    )
    
    return {
        "cv_scores": cv_scores.tolist(),
        "cv_mean": float(cv_scores.mean()),
        "cv_std": float(cv_scores.std()),
        "cv_folds": cv_folds,
        "cv_scoring": cv_scoring,
    }


# =============================================================================
# Test set evaluation
# =============================================================================
def evaluate_on_test(
    model: Any,
    test_data: pd.DataFrame,
    target_column: str,
) -> Metrics:

    X_test = test_data.drop(columns=[target_column]).select_dtypes(include=[np.number])
    y_test = test_data[target_column]
    
    y_pred = model.predict(X_test)
    
    metrics: Metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
    }
    
    return metrics


# =============================================================================
# Confusion matrix
# =============================================================================
def generate_confusion_matrix(
    model: Any,
    test_data: pd.DataFrame,
    target_column: str,
) -> None:

    X_test = test_data.drop(columns=[target_column]).select_dtypes(include=[np.number])
    y_test = test_data[target_column]
    
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=True,
        square=True,
        ax=ax,
        xticklabels=["Low Risk", "High Risk"],
        yticklabels=["Low Risk", "High Risk"],
    )
    ax.set_xlabel("Predicted Label", fontsize=12)
    ax.set_ylabel("True Label", fontsize=12)
    ax.set_title("Confusion Matrix - Test Set", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    
    # Save to file
    output_path = Path("docs/plots/confusion_matrix.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# Feature importance
# =============================================================================
def compute_feature_importance(
    model: Any,
    train_data: pd.DataFrame,
    target_column: str,
    top_n: int = 15,
) -> None:

    if not hasattr(model, "feature_importances_"):
        # Create empty plot if model doesn't support feature importance
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(
            0.5, 0.5,
            "Model does not support feature importance",
            ha="center", va="center",
            fontsize=14,
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
    else:
        X = train_data.drop(columns=[target_column]).select_dtypes(include=[np.number])
        feature_names = X.columns.tolist()
        importances = model.feature_importances_
        
        # Create DataFrame and sort
        importance_df = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        }).sort_values("importance", ascending=False).head(top_n)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.barh(
            range(len(importance_df)),
            importance_df["importance"].values,
            color="steelblue",
        )
        ax.set_yticks(range(len(importance_df)))
        ax.set_yticklabels(importance_df["feature"].values)
        ax.invert_yaxis()
        ax.set_xlabel("Importance", fontsize=12)
        ax.set_title(
            f"Top {top_n} Feature Importances",
            fontsize=14,
            fontweight="bold",
        )
        ax.grid(axis="x", alpha=0.3)
        plt.tight_layout()
    
    # Save to file
    output_path = Path("docs/plots/feature_importance.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# SHAP values (optional)
# =============================================================================
def compute_shap_values(
    model: Any,
    train_data: pd.DataFrame,
    target_column: str,
    max_samples: int = 100,
) -> None:

    try:
        import shap
        
        X = train_data.drop(columns=[target_column]).select_dtypes(include=[np.number])
        
        # Sample data if too large
        if len(X) > max_samples:
            X_sample = X.sample(n=max_samples, random_state=42)
        else:
            X_sample = X
        
        # Create explainer based on model type
        if isinstance(model, RandomForestClassifier):
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.Explainer(model.predict, X_sample)
        
        shap_values = explainer(X_sample)
        
        # Create summary plot
        fig = plt.figure(figsize=(10, 8))
        shap.summary_plot(shap_values, X_sample, show=False)
        plt.title("SHAP Summary Plot", fontsize=14, fontweight="bold", pad=20)
        plt.tight_layout()
        
    except ImportError:
        # If SHAP is not installed, create placeholder
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(
            0.5, 0.5,
            "SHAP library not installed\nInstall with: pip install shap",
            ha="center", va="center",
            fontsize=14,
        )
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
    
    # Save to file
    output_path = Path("docs/plots/shap_summary.png")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# =============================================================================
# Model versioning
# =============================================================================
def create_model_version_log(
    test_metrics: Metrics,
    model_name: str = "best_model.pkl",
    version: str = "1.0",
) -> pd.DataFrame:

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "timestamp": timestamp,
        "model_name": model_name,
        "accuracy": test_metrics.get("accuracy", 0.0),
        "f1_score": test_metrics.get("f1_score", 0.0),
        "version": version,
    }
    
    return pd.DataFrame([log_entry])


# =============================================================================
# Select best model
# =============================================================================
def select_best_model(
    baseline_model: Any,
    automl_model: Any,
    custom_model: Any,
    model_comparison: Dict[str, Any],
) -> Any:

    best_model_name = model_comparison["best_model_by_f1"]
    
    model_map = {
        "baseline": baseline_model,
        "automl": automl_model,
        "custom": custom_model,
    }
    
    return model_map[best_model_name]
