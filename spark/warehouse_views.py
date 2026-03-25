from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("WarehouseViews") \
    .config("spark.sql.warehouse.dir", "/app/spark-warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# -----------------------------------
# Create warehouse database
# -----------------------------------
spark.sql("CREATE DATABASE IF NOT EXISTS warehouse")

# -----------------------------------
# Drop existing view (safe re-runs)
# -----------------------------------
spark.sql("DROP VIEW IF EXISTS warehouse.employee_vw")

# -----------------------------------
# Create secure warehouse view
# IMPORTANT: reference ONLY persistent tables
# -----------------------------------
spark.sql("""
    CREATE VIEW warehouse.employee_vw AS
    SELECT
        id,

        -- Mask PII
        '****' AS name_masked,

        department,

        -- Hash sensitive data
        sha2(CAST(salary AS STRING), 256) AS salary_hash,

        start_date
    FROM target.employee_dim
    WHERE is_current = true
""")

print("✅ Warehouse secure view created: warehouse.employee_vw")

spark.stop()