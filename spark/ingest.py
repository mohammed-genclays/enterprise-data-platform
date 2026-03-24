from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("EnterpriseIngestion") \
    .getOrCreate()

# Read CSV from mounted volume
df = spark.read.option("header", True).csv("/app/data/employee.csv")

print("=== RAW DATA ===")
df.show()

print("=== SCHEMA ===")
df.printSchema()

spark.stop()
