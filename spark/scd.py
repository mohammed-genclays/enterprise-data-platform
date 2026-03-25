from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_date, sha2, concat_ws
from pyspark.sql.types import DateType
import os
import shutil

# -----------------------------------
# Spark session
# -----------------------------------
spark = SparkSession.builder \
    .appName("SCDFramework") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Read staging data
# -----------------------------------
df_stage = spark.sql("SELECT * FROM staging.employee")

# Hash for change detection
df_stage = df_stage.withColumn(
    "hash",
    sha2(concat_ws("||", col("name"), col("department"), col("salary")), 256)
)

# -----------------------------------
# Create target database
# -----------------------------------
spark.sql("CREATE DATABASE IF NOT EXISTS target")

TARGET_PATH = "/app/spark-warehouse/target.db/employee_dim"

# -----------------------------------
# SCD TYPE 1 (Overwrite)
# -----------------------------------
def scd_type_1():
    spark.sql("DROP TABLE IF EXISTS target.employee_dim")

    if os.path.exists(TARGET_PATH):
        shutil.rmtree(TARGET_PATH)

    df_stage.write \
        .mode("overwrite") \
        .format("parquet") \
        .saveAsTable("target.employee_dim")

# -----------------------------------
# SCD TYPE 2 (History)
# -----------------------------------
def scd_type_2():
    # Clean metadata + physical location (VERY IMPORTANT)
    spark.sql("DROP TABLE IF EXISTS target.employee_dim")

    if os.path.exists(TARGET_PATH):
        shutil.rmtree(TARGET_PATH)

    # Create empty target table
    spark.sql("""
        CREATE TABLE target.employee_dim (
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
    df_new = df_stage.withColumn("start_date", current_date()) \
        .withColumn("end_date", lit(None).cast(DateType())) \
        .withColumn("is_current", lit(True))

    # First load (table is empty)
    df_new.write.mode("append").saveAsTable("target.employee_dim")

# -----------------------------------
# Execute SCD Type 2 (default)
# -----------------------------------
scd_type_2()

spark.stop()
