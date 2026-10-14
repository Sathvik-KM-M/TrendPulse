from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/home/mglocadmin/TrendPulse"
VENV_PYTHON = f"{PROJECT_DIR}/tenv/bin/python"

default_args = {
    "owner": "sathvik",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="trendpulse_pipeline",
    description="TrendPulse: ingest → bronze → silver → gold",
    default_args=default_args,
    start_date=datetime(2026, 10, 13),
    schedule="*/30 * * * *",
    catchup=False,
    tags=["trendpulse", "kafka", "spark"],
) as dag:

    produce = BashOperator(
        task_id="produce_to_kafka",
        bash_command=f"cd {PROJECT_DIR} && timeout 60 {VENV_PYTHON} -m src.ingestion.kafka_producer || true",
    )

    consume_to_bronze = BashOperator(
        task_id="consume_to_bronze",
        bash_command=f"cd {PROJECT_DIR} && timeout 60 {VENV_PYTHON} -m src.processing.spark_consumer || true",
    )

    bronze_to_silver = BashOperator(
        task_id="bronze_to_silver",
        bash_command=f"cd {PROJECT_DIR} && {VENV_PYTHON} -m src.processing.silver_worker",
    )

    silver_to_gold = BashOperator(
        task_id="silver_to_gold",
        bash_command=f"cd {PROJECT_DIR} && {VENV_PYTHON} -m src.processing.gold_worker",
    )

    produce >> consume_to_bronze >> bronze_to_silver >> silver_to_gold
