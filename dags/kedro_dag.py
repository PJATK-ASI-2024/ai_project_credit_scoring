from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 12, 3),
    "retries": 1,
}

with DAG(
    dag_id="kedro_project_pipeline",
    default_args=default_args,
    schedule_interval="0 8 * * *",  # codziennie o 8:00
    catchup=False,
    tags=["kedro", "mlops"],
) as dag:

    eda = BashOperator(
        task_id="eda_pipeline",
        bash_command="cd /workspace/ai-credit-scoring && kedro run --pipeline=eda"
    )

    preprocessing = BashOperator(
        task_id="preprocessing_pipeline",
        bash_command="cd /workspace/ai-credit-scoring && kedro run --pipeline=preprocessing"
    )

    modeling = BashOperator(
        task_id="modeling_pipeline",
        bash_command="cd /workspace/ai-credit-scoring && kedro run --pipeline=modeling"
    )

    evaluation = BashOperator(
        task_id="evaluation_pipeline",
        bash_command="cd /workspace/ai-credit-scoring && kedro run --pipeline=evaluation"
    )

    eda >> preprocessing >> modeling >> evaluation
