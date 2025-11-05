from kedro.pipeline import Pipeline, node
from .nodes import (
    basic_stats, save_json, plot_missingness, correlation_heatmap,
    numeric_distributions, categorical_counts, make_eda_report
)

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        node(
            func=basic_stats,
            inputs="credit_raw",
            outputs="eda_stats",
            name="eda_basic_stats",
        ),
        node(
            func=plot_missingness,
            inputs=dict(df="credit_raw", out_path="params:eda.paths.missing_png"),
            outputs=None,
            name="eda_plot_missingness",
        ),
        node(
            func=correlation_heatmap,
            inputs=dict(df="credit_raw", out_path="params:eda.paths.corr_png"),
            outputs=None,
            name="eda_correlation_heatmap",
        ),
        node(
            func=numeric_distributions,
            inputs=dict(df="credit_raw", out_dir="params:eda.paths.num_dir"),
            outputs="eda_num_plots",
            name="eda_numeric_distributions",
        ),
        node(
            func=categorical_counts,
            inputs=dict(df="credit_raw", out_dir="params:eda.paths.cat_dir"),
            outputs="eda_cat_plots",
            name="eda_categorical_counts",
        ),
        node(
            func=save_json,
            inputs=dict(obj="eda_stats", filepath="params:eda.paths.stats_json"),
            outputs=None,
            name="eda_save_stats_json",
        ),
        node(
            func=make_eda_report,
            inputs=dict(
                stats="eda_stats",
                paths="params:eda.paths",
                outfile_md="params:eda.paths.report_md",
            ),
            outputs=None,
            name="eda_make_report_md",
        ),
    ])
