"""Evaluation pipeline for model testing and analysis."""

from kedro.pipeline import Pipeline, node

from .nodes import (
    compute_feature_importance,
    compute_shap_values,
    create_model_version_log,
    cross_validate_model,
    evaluate_on_test,
    generate_confusion_matrix,
    select_best_model,
)


def create_pipeline(**kwargs) -> Pipeline:
    """Create evaluation pipeline."""
    return Pipeline(
        [
            # Select best model from modeling outputs
            node(
                func=select_best_model,
                inputs=[
                    "baseline_model",
                    "automl_model",
                    "custom_model",
                    "model_comparison",
                ],
                outputs="best_model",
                name="select_best_model_node",
            ),
            # Cross-validation on best model
            node(
                func=cross_validate_model,
                inputs=[
                    "best_model",
                    "train_data",
                    "params:modeling.target_column",
                    "params:evaluation.cv_folds",
                    "params:evaluation.cv_scoring",
                    "params:evaluation.random_state",
                ],
                outputs="cv_scores",
                name="cross_validate_node",
            ),
            # Evaluate on test set
            node(
                func=evaluate_on_test,
                inputs=[
                    "best_model",
                    "test_data",
                    "params:modeling.target_column",
                ],
                outputs="test_metrics",
                name="evaluate_test_node",
            ),
            # Generate confusion matrix
            node(
                func=generate_confusion_matrix,
                inputs=[
                    "best_model",
                    "test_data",
                    "params:modeling.target_column",
                ],
                outputs=None,
                name="confusion_matrix_node",
            ),
            # Compute feature importance
            node(
                func=compute_feature_importance,
                inputs=[
                    "best_model",
                    "train_data",
                    "params:modeling.target_column",
                ],
                outputs=None,
                name="feature_importance_node",
            ),
            # Compute SHAP values (optional)
            node(
                func=compute_shap_values,
                inputs=[
                    "best_model",
                    "train_data",
                    "params:modeling.target_column",
                    "params:evaluation.shap_max_samples",
                ],
                outputs=None,
                name="shap_values_node",
            ),
            # Create model version log
            node(
                func=create_model_version_log,
                inputs=[
                    "test_metrics",
                    "params:evaluation.model_name",
                    "params:evaluation.version",
                ],
                outputs="model_versions",
                name="model_version_log_node",
            ),
        ]
    )
