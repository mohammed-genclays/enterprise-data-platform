from pyspark.sql import SparkSession
import yaml

# -----------------------------------
# Spark session
# -----------------------------------
spark = SparkSession.builder \
    .appName("WarehouseViews") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Load metadata
# -----------------------------------
with open("/app/config/pipelines.yaml") as f:
    config = yaml.safe_load(f)

# -----------------------------------
# Create warehouse database
# -----------------------------------
spark.sql("CREATE DATABASE IF NOT EXISTS warehouse")

# -----------------------------------
# Create warehouse views per pipeline
# -----------------------------------
for pipeline in config["pipelines"]:

    pipeline_name = pipeline["pipeline_name"]
    target_table = pipeline["target_table"]

    view_name = f"warehouse.{pipeline_name}_vw"

    print(f"=== Creating warehouse view: {view_name} ===")

    # Drop existing view (safe re-runs)
    spark.sql(f"DROP VIEW IF EXISTS {view_name}")

    # Create secure warehouse view
    spark.sql(f"""
        CREATE VIEW {view_name} AS
        SELECT
            id,

            -- Mask PII
            '****' AS name_masked,

            department,

            -- Hash sensitive columns
            sha2(CAST(salary AS STRING), 256) AS salary_hash,

            start_date
        FROM {target_table}
        WHERE is_current = true
    """)

    print(f"✅ Warehouse secure view created: {view_name}")

spark.stop()