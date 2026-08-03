from __future__ import annotations

from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG


PROJECT_DIR = "/opt/airflow/project"


default_args = {
    "owner": "sam",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="music_streaming_pipeline",
    description="Orchestrates the music streaming analytics pipeline",
    default_args=default_args,
    start_date=datetime(2026, 8, 1),
    schedule=None,
    catchup=False,
    tags=["music-streaming", "snowflake", "dbt", "data-quality"],
) as dag:

    start_pipeline = BashOperator(
        task_id="start_pipeline",
        bash_command="""
        echo "Starting music streaming analytics pipeline"
        echo "Execution date: {{ ds }}"
        """,
    )

    verify_project_mount = BashOperator(
        task_id="verify_project_mount",
        bash_command=f"""
        set -e

        echo "Checking project mount..."
        test -d {PROJECT_DIR}
        test -d {PROJECT_DIR}/ingestion
        test -d {PROJECT_DIR}/music_analytics
        test -f {PROJECT_DIR}/tests/validate_metadata_gx.py

        echo "Project files are available inside Airflow."
        """,
    )

    verify_input_data = BashOperator(
        task_id="verify_input_data",
        bash_command=f"""
        set -e

        DATA_FILE="{PROJECT_DIR}/data/processed/music_metadata_clean.parquet"

        echo "Checking processed metadata file..."

        if [ ! -f "$DATA_FILE" ]; then
            echo "Required input file was not found: $DATA_FILE"
            exit 1
        fi

        ls -lh "$DATA_FILE"
        echo "Processed metadata file exists."
        """,
    )

    pipeline_complete = BashOperator(
        task_id="pipeline_complete",
        bash_command="""
        echo "Airflow smoke test completed successfully."
        echo "The project mount and input data are accessible."
        """,
    )

    (
        start_pipeline
        >> verify_project_mount
        >> verify_input_data
        >> pipeline_complete
    )