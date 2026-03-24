from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, initcap, when
from pyspark.sql.types import IntegerType

# -----------------------------------
# Spark session with warehouse support
# -----------------------------------
spark = SparkSession.builder \
    .appName("EnterpriseTransformations") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Read raw data
# -----------------------------------
df = spark.read.option("header", True).csv("/app/data/employee.csv")

print("=== RAW DATA ===")
df.show()

# -----------------------------------
# Transformations
# -----------------------------------
df_clean = df.withColumn(
    "name", initcap(trim(col("name")))
)

df_clean = df_clean.withColumn(
    "salary",
    when(col("salary").isNull(), 0).otherwise(col("salary")).cast(IntegerType())
)

df_clean = df_clean.withColumn(
    "id", col("id").cast(IntegerType())
)

df_clean = df_clean.filter(col("id").isNotNull())

print("=== CLEAN DATA ===")
df_clean.show()

# -----------------------------------
# Create STAGING database & table
# -----------------------------------
spark.sql("CREATE DATABASE IF NOT EXISTS staging")

df_clean.write \
    .mode("overwrite") \
    .format("parquet") \
    .saveAsTable("staging.employee")

print("=== DATA WRITTEN TO STAGING TABLE ===")

# -----------------------------------
# Read back from staging (validation)
# -----------------------------------
df_stage = spark.sql("SELECT * FROM staging.employee")

print("=== STAGING TABLE DATA ===")
df_stage.show()

spark.stop()