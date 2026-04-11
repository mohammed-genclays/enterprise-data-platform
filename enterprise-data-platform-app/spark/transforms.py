from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, initcap, when
from pyspark.sql.types import IntegerType
import yaml
import os
import shutil

# -----------------------------------
# Spark session with warehouse support
# -----------------------------------
spark = (
    SparkSession.builder
    .appName("EnterpriseTransformations")
    .config("spark.sql.warehouse.dir", "/tmp/spark-warehouse")
    .config("javax.jdo.option.ConnectionURL",
            "jdbc:derby:memory:metastore_db;create=true")
    .config("spark.hadoop.fs.gs.impl",
            "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem")
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl",
            "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS")
    .config("spark.hadoop.google.cloud.auth.service.account.enable", "true")
    .enableHiveSupport()
    .getOrCreate()
)


# -----------------------------------
# Load metadata
# -----------------------------------
with open("/app/config/pipelines.yaml") as f:
    config = yaml.safe_load(f)

# -----------------------------------
# Process each pipeline
# -----------------------------------
for pipeline in config["pipelines"]:

    print(f"=== Processing pipeline: {pipeline['pipeline_name']} ===")

    source_path = pipeline["source"]["path"]
    staging_table = pipeline["staging_table"]

    # -----------------------------------
    # Read raw data
    # -----------------------------------
    df = spark.read.option("header", True).csv(source_path)

    print("=== RAW DATA ===")
    df.show()

    # -----------------------------------
    # Transformations (YOUR ORIGINAL LOGIC)
    # -----------------------------------
    df_clean = df.withColumn(
        "name", initcap(trim(col("name")))
    )

    df_clean = df_clean.withColumn(
        "salary",
        when(col("salary").isNull(), 0)
        .otherwise(col("salary"))
        .cast(IntegerType())
    )

    df_clean = df_clean.withColumn(
        "id", col("id").cast(IntegerType())
    )

    df_clean = df_clean.filter(col("id").isNotNull())

    print("=== CLEAN DATA ===")
    df_clean.show()

    # -----------------------------------
    # Create STAGING database
    # -----------------------------------
    spark.sql("CREATE DATABASE IF NOT EXISTS staging")

    # -----------------------------------
    # Idempotent staging write
    # -----------------------------------
    spark.sql(f"DROP TABLE IF EXISTS {staging_table}")

    table_name = staging_table.split(".")[1]
    table_path = f"/app/spark-warehouse/staging.db/{table_name}"

    if os.path.exists(table_path):
        shutil.rmtree(table_path)

    df_clean.write \
        .mode("overwrite") \
        .format("parquet") \
        .saveAsTable(staging_table)

    print(f"=== DATA WRITTEN TO {staging_table} ===")

    # -----------------------------------
    # Read-back validation
    # -----------------------------------
    df_stage = spark.sql(f"SELECT * FROM {staging_table}")

    print("=== STAGING TABLE DATA ===")
    df_stage.show()

spark.stop()