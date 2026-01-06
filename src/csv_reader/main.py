from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("CSV to Parquet Writer") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

print(f"Spark version: {spark.version}")

csv_path = "/shared/data/ocorrencias.csv"
# output_path = "/tmp/parquet"  # Use the path that works in the container!
# output_path = "/shared/output/ocorrencias_parquet"
output_path = "/shared/output/ocorrencias_parquet"

print(f"Reading CSV: {csv_path}")
df = spark.read.csv(
    path=csv_path,
    header=True,
    sep=";",
    inferSchema=True,
    encoding="utf-8"
)

print(f"Writing Parquet to: {output_path}")
df.write.mode("overwrite").parquet(output_path)

print("CSV successfully written to Parquet.")
