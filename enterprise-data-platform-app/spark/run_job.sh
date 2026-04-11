#!/bin/bash
set -e

echo "Starting Spark ETL job..."

JARS=/opt/spark/jars/gcs-connector.jar
SPARK_SUBMIT=/opt/spark/bin/spark-submit

$SPARK_SUBMIT --jars $JARS /app/spark/transforms.py
$SPARK_SUBMIT --jars $JARS /app/spark/scd.py
$SPARK_SUBMIT --jars $JARS /app/spark/warehouse_views.py
$SPARK_SUBMIT --jars $JARS /app/spark/export_dashboard.py

echo "Spark ETL job completed."