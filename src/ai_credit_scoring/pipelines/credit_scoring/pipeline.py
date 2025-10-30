"""
This is a boilerplate pipeline 'credit_scoring'
generated using Kedro 1.0.0
"""

from kedro.pipeline import Pipeline, node
from .nodes import load_data, preprocess_data

def create_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=load_data,
                inputs="credit_raw",
                outputs="credit_intermediate",
                name="load_credit_data",
            ),
            node(
                func=preprocess_data,
                inputs="credit_intermediate",
                outputs="credit_processed",
                name="preprocess_credit_data",
            ),
        ]
    )
