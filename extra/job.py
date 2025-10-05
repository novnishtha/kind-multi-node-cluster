import os
os.environ["PYSPARK_PYTHON"] = "python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time

#  Initialize Spark Session
spark = SparkSession.builder.appName("DataAnalysis2").getOrCreate()

customers_df = spark.read.parquet("C:\\Users\\Dell\\PycharmProjects\\nis-spark-experiments\\docker_transactions\\data_skew\\customers.parquet")
transactions_df = spark.read.parquet("C:\\Users\\Dell\\PycharmProjects\\nis-spark-experiments\\docker_transactions\\data_skew\\transactions.parquet")

transactions_df.printSchema()
customers_df.printSchema()



"""print("--- Original Transactions Schema ---")
transactions_df.printSchema()

transactions_with_date = transactions_df.withColumn("date", to_date(col("date")))

print("\n--- Transactions Schema After Date Conversion ---")
transactions_with_date.printSchema()


# --- Now, run your analysis on the corrected DataFrame ---
print("\n--- Using DataFrame API ---")
# Find the total amount spent on 'Entertainment' in 2018
entertainment_2018_df = transactions_with_date \
    .filter((col("expense_type") == "Entertainment") & (year(col("date")) == 2018)) \
    .groupBy("cust_id") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_entertainment_spend")


print("Total Entertainment Spend in 2018:")
entertainment_2018_df.show(5)
time.sleep(300)
spark.stop()"""
