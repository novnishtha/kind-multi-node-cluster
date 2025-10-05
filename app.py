import os
os.environ["PYSPARK_PYTHON"] = "python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, to_date
import time

#  Initialize Spark Session
spark = SparkSession.builder.appName("DataAnalysis").getOrCreate()

#customers_df = spark.read.parquet("/app/data_skew/customers.parquet")
#transactions_df = spark.read.parquet("/app/data_skew/transactions.parquet")
customers_df = spark.read.parquet("C:\\Users\\Dell\\PycharmProjects\\nis-spark-experiments\\docker_transactions\\data_skew\\customers.parquet")
transactions_df = spark.read.parquet("C:\\Users\\Dell\\PycharmProjects\\nis-spark-experiments\\docker_transactions\\data_skew\\transactions.parquet")

print("--- Original Transactions Schema ---")
transactions_df.printSchema()

transactions_with_date = transactions_df.withColumn("date", to_date(col("date")))

print("\n--- Transactions Schema After Date Conversion ---")
transactions_with_date.printSchema()

print("\n--- Customers Schema ---")
customers_df.printSchema()

# Find the total amount spent on 'Entertainment' in 2018
entertainment_2018_df = transactions_with_date \
    .filter((col("expense_type") == "Entertainment") & (year(col("date")) == 2018)) \
    .groupBy("cust_id") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_entertainment_spend")

print("Total Entertainment Spend in 2018:")
entertainment_2018_df.show(5)

# Find the top 3 cities by total transaction amount
start_time_top_cities = time.time()
top_cities_by_spend = transactions_with_date.groupBy("city") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_transaction_amount") \
    .orderBy(col("total_transaction_amount").desc()) \
    .limit(3)

print("\nTop 3 Cities by Total Transaction Amount:")
top_cities_by_spend.show()
end_time_top_cities = time.time()
print(f"Time taken for 'Top 3 Cities' analysis: {end_time_top_cities - start_time_top_cities:.2f} seconds")

#time.sleep(540)
#spark.stop()
