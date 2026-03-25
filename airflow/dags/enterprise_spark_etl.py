from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    dag_id="enterprise_spark_etl",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,   # manual trigger
    catchup=False,
    tags=["spark", "etl", "staging"]
) as dag:

    spark_transform = BashOperator(
        task_id="spark_ingest_and_transform",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/transforms.py"
    )

    spark_transform