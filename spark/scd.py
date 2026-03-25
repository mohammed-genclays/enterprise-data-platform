from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_date, sha2, concat_ws
from pyspark.sql.types import DateType
import os
import shutil
import yaml

# -----------------------------------
# Spark session
# -----------------------------------
spark = SparkSession.builder \
    .appName("SCDFramework") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Load metadata
# -----------------------------------
with open("/app/config/pipelines.yaml") as f:
    config = yaml.safe_load(f)

# -----------------------------------
# Create target database
# -----------------------------------
spark.sql("CREATE DATABASE IF NOT EXISTS target")

# -----------------------------------
# Process each pipeline
# -----------------------------------
for pipeline in config["pipelines"]:

    staging_table = pipeline["staging_table"]
    target_table = pipeline["target_table"]
    scd_type = pipeline.get("scd_type", 2)

    target_db, target_tbl = target_table.split(".")
    target_path = f"/app/spark-warehouse/{target_db}.db/{target_tbl}"

    print(f"=== Processing SCD for {target_table} (Type {scd_type}) ===")

    # -----------------------------------
    # Read staging data
    # -----------------------------------
    df_stage = spark.sql(f"SELECT * FROM {staging_table}")

    # Hash for change detection
    df_stage = df_stage.withColumn(
        "hash",
        sha2(
            concat_ws("||",
                col("name"),
                col("department"),
                col("salary").cast("string")
            ),
            256
        )
    )

    # -----------------------------------
    # SCD TYPE 1 (Overwrite)
    # -----------------------------------
    if scd_type == 1:

        spark.sql(f"DROP TABLE IF EXISTS {target_table}")

        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        df_stage.write \
            .mode("overwrite") \
            .format("parquet") \
            .saveAsTable(target_table)

        print(f"✅ SCD Type 1 load completed for {target_table}")

    # -----------------------------------
    # SCD TYPE 2 (History)
    # -----------------------------------
    elif scd_type == 2:

        # Clean metadata + physical storage (IDEMPOTENT)
        spark.sql(f"DROP TABLE IF EXISTS {target_table}")

        if os.path.exists(target_path):
            shutil.rmtree(target_path)

        # Create empty target table
        spark.sql(f"""
            CREATE TABLE {target_table} (
                id INT,
                name STRING,
                department STRING,
                salary INT,
                start_date DATE,
                end_date DATE,
                is_current BOOLEAN,
                hash STRING
            )
            USING PARQUET
        """)

        # Prepare new records
        df_new = df_stage \
            .withColumn("start_date", current_date()) \
            .withColumn("end_date", lit(None).cast(DateType())) \
            .withColumn("is_current", lit(True))

        # First load
        df_new.write.mode("append").saveAsTable(target_table)

        print(f"✅ SCD Type 2 load completed for {target_table}")

    else:
        raise Exception(f"Unsupported SCD type: {scd_type}")

spark.stop()