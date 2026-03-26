from pyspark.sql import SparkSession
import yaml
import os

spark = SparkSession.builder \
    .appName("ExportDashboardData") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Load metadata
# -----------------------------------
with open("/app/config/pipelines.yaml") as f:
    config = yaml.safe_load(f)

# -----------------------------------
# Export each pipeline's warehouse view
# -----------------------------------
os.makedirs("/app/data", exist_ok=True)

for pipeline in config["pipelines"]:
    pipeline_name = pipeline["pipeline_name"]
    view_name = f"warehouse.{pipeline_name}_vw"
    output_path = f"/app/data/dashboard_{pipeline_name}.csv"

    print(f"Exporting view {view_name} to {output_path}")

    df = spark.sql(f"SELECT * FROM {view_name}")
    df.coalesce(1).write.mode("overwrite").option("header", True).csv(output_path)

    print(f"✅ Export completed for {view_name}")

spark.stop()
