"""Project pipelines."""
from __future__ import annotations

from kedro.pipeline import Pipeline

from .pipelines.credit_scoring import (
    create_pipeline as create_credit_scoring_pipeline,
)
from .pipelines.eda import create_pipeline as create_eda_pipeline
from .pipelines.modeling import (
    create_pipeline as create_modeling_pipeline,
)
from .pipelines.preprocessing import (
    create_pipeline as create_preprocessing_pipeline,
)


def register_pipelines() -> dict[str, Pipeline]:
    """Register the project's pipelines.

    Returns:
        A mapping from pipeline names to ``Pipeline`` objects.
    """
    pipelines: dict[str, Pipeline] = {
        "credit_scoring": create_credit_scoring_pipeline(),
        "eda": create_eda_pipeline(),
        "preprocessing": create_preprocessing_pipeline(),
        "modeling": create_modeling_pipeline(),
    }

    pipelines["__default__"] = sum(pipelines.values(), Pipeline([]))
    return pipelines
