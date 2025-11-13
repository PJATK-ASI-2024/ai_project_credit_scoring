from kedro.pipeline import Pipeline, node, pipeline
from .nodes import (
    clean_data,
    scale_data,
    split_data,
    validate_clean,
    validate_scaled,
    validate_split,
    build_preprocessing_report,
)


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                clean_data,
                inputs=["credit_raw", "params:preprocessing"],
                outputs="clean_data",
                name="clean_data_node",
            ),
            node(
                validate_clean,
                inputs=["clean_data", "params:preprocessing"],
                outputs="clean_quality_report",
                name="validate_clean_node",
            ),
            node(
                scale_data,
                inputs=["clean_data", "params:preprocessing"],
                outputs="scaled_data",
                name="scale_data_node",
            ),
            node(
                validate_scaled,
                inputs=["scaled_data", "params:preprocessing"],
                outputs="scaled_quality_report",
                name="validate_scaled_node",
            ),
            node(
                split_data,
                inputs=["scaled_data", "params:preprocessing"],
                outputs=["train_data", "val_data", "test_data"],
                name="split_data_node",
            ),
            node(
                validate_split,
                inputs=["train_data", "val_data", "test_data", "params:preprocessing"],
                outputs="split_quality_report",
                name="validate_split_node",
            ),
            node(
                build_preprocessing_report,
                inputs=[
                    "credit_raw",          # PRZED
                    "clean_data",          # po cleaningu
                    "scaled_data",         # po skalowaniu
                    "clean_quality_report",
                    "scaled_quality_report",
                    "split_quality_report",
                    "params:preprocessing",
                ],
                outputs="preprocessing_report",
                name="build_preprocessing_report_node",
            ),
        ]
    )
