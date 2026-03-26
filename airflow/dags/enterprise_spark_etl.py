from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="enterprise_spark_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False
) as dag:

    transform = BashOperator(
        task_id="spark_transform",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/transforms.py"
    )

    scd = BashOperator(
        task_id="spark_scd",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/scd.py"
    )

    warehouse = BashOperator(
        task_id="spark_warehouse",
        bash_command="docker exec spark /opt/spark/bin/spark-submit /app/spark/warehouse_views.py"
    )
    export_dashboard_data = BashOperator(
    task_id="export_dashboard_data",
    bash_command="""
    docker exec spark /opt/spark/bin/spark-sql -e "
    SELECT * FROM warehouse.employee_pipeline_vw
    " > /app/data/dashboard_employee_pipeline.csv
    """
    )
    spark_transform >> spark_scd >> spark_warehouse >> export_dashboard_data
