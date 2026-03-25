from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="enterprise_spark_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    spark_transform = BashOperator(
        task_id="spark_transform",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/transforms.py"
    )

    spark_scd = BashOperator(
        task_id="spark_scd",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/scd.py"
    )

    spark_transform >> spark_scd