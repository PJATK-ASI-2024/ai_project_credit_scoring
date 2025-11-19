from kedro.pipeline import Pipeline, node

from .nodes import (
    train_baseline,
    train_automl,
    train_custom,
    evaluate_models,
)


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_baseline,
                inputs=["train_data", "val_data", "params:modeling.target_column"],
                outputs=["baseline_model", "baseline_metrics"],
                name="train_baseline_node",
            ),
            node(
                func=train_automl,
                inputs=["train_data", "val_data", "params:modeling.target_column"],
                outputs=["automl_model", "automl_metrics", "automl_results"],
                name="train_automl_node",
            ),
            node(
                func=train_custom,
                inputs=["train_data", "val_data", "params:modeling.target_column"],
                outputs=["custom_model", "custom_metrics"],
                name="train_custom_node",
            ),
            node(
                func=evaluate_models,
                inputs=["baseline_metrics", "automl_metrics", "custom_metrics"],
                outputs="model_comparison",
                name="evaluate_models_node",
            ),
        ]
    )
