from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, initcap, when
from pyspark.sql.types import IntegerType

spark = SparkSession.builder \
    .appName("EnterpriseTransformations") \
    .getOrCreate()

# Read raw data
df = spark.read.option("header", True).csv("/app/data/employee.csv")

print("=== RAW DATA ===")
df.show()

# -----------------------------
# Transformations
# -----------------------------

# Trim & standardize name
df_clean = df.withColumn(
    "name",
    initcap(trim(col("name")))
)

# Handle null salary (default 0)
df_clean = df_clean.withColumn(
    "salary",
    when(col("salary").isNull(), 0).otherwise(col("salary")).cast(IntegerType())
)

# Cast id
df_clean = df_clean.withColumn("id", col("id").cast(IntegerType()))

# Filter invalid records (id is null)
df_clean = df_clean.filter(col("id").isNotNull())

print("=== CLEAN DATA ===")
df_clean.show()

print("=== CLEAN SCHEMA ===")
df_clean.printSchema()

spark.stop()
