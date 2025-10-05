import os
os.environ["PYSPARK_PYTHON"] = "python"
os.environ["PYSPARK_DRIVER_PYTHON"] = "python"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, to_date
import time

# Initialize Spark Session
spark = SparkSession.builder.appName("JobTransformations").getOrCreate()

# Load DataFrames using relative paths
customers_df = spark.read.parquet("/app/data_skew/customers.parquet")
transactions_df = spark.read.parquet("/app/data_skew/transactions.parquet")

print("--- Original Transactions Schema ---")
transactions_df.printSchema()

# Time tracking for date conversion
start_time_date_conversion = time.time()
transactions_with_date = transactions_df.withColumn("date", to_date(col("date")))
end_time_date_conversion = time.time()
print(f"\nTime taken for date conversion: {end_time_date_conversion - start_time_date_conversion:.2f} seconds")

print("\n--- Transactions Schema After Date Conversion ---")
transactions_with_date.printSchema()

print("\n--- Customers Schema ---")
customers_df.printSchema()

# --- Now, running analysis with time tracking ---
print("\n--- Using DataFrame API ---")

# Time tracking for the 'Entertainment' analysis (groupBy one column: cust_id)
start_time_entertainment = time.time()
entertainment_2018_df = transactions_with_date \
    .filter((col("expense_type") == "Entertainment") & (year(col("date")) == 2018)) \
    .groupBy("cust_id") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_entertainment_spend")
entertainment_2018_df.show(5)
end_time_entertainment = time.time()
print(f"Time taken for 'Entertainment' analysis: {end_time_entertainment - start_time_entertainment:.2f} seconds")  #8.49 sec

# Time tracking for 'Gambling' analysis (groupBy two columns: cust_id and city)
print("\n--- Finding Top Gambling Spenders ---")
start_time_gamb_spenders = time.time()
top_gamb_spenders_df = transactions_with_date.filter(col("expense_type") == "Gambling") \
    .groupBy("cust_id", "city") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_gamb_spend") \
    .orderBy(col("total_gamb_spend").desc())
top_gamb_spenders_df.show(7)
end_time_gamb_spenders = time.time()
print(f"Time taken for 'Gambling' analysis: {end_time_gamb_spenders - start_time_gamb_spenders:.2f} seconds")   #8.27 sec

# Time tracking for 'Average Monthly Spending' analysis
print("\n--- Calculating Average Monthly Spending ---")
start_time_avg_monthly_spend = time.time()
avg_monthly_spend_df = transactions_with_date \
    .groupBy("cust_id", "year", "month") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "monthly_spend") \
    .groupBy("cust_id") \
    .agg({"monthly_spend": "avg"}) \
    .withColumnRenamed("avg(monthly_spend)", "average_monthly_spend")
avg_monthly_spend_df.show(5)
end_time_avg_monthly_spend = time.time()
print(f"Time taken for 'Average Monthly Spending' analysis: {end_time_avg_monthly_spend - start_time_avg_monthly_spend:.2f} seconds")   #39.05 sec

print("\n--- Joining Transactions with Customers and Aggregating ---")
start_time_join = time.time()
customers_with_transactions = transactions_with_date.join(customers_df, on="cust_id")

# Time tracking for Count after join
start_count_time = time.time()
print(f"\n--- The Joint DF has {customers_with_transactions.count()} rows. --- \n")
#customers_with_transactions.show()
end_count_time = time.time()
print(f"Time taken for Count of rows: {end_count_time - start_count_time:.2f} seconds")   #3.00 sec

# Time tracking for Aggregating after Join (amt spend by people above 30 age)
total_spend_over_30 = customers_with_transactions.filter(col("age") > 30) \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_spend_for_over_30")
total_spend_over_30.show()
end_time_join = time.time()
print(f"Time taken for 'Join and Aggregate' analysis: {end_time_join - start_time_join:.2f} seconds")   #4.65 sec

# Time tracking for 'Top 3 Cities' analysis
print("\n--- Finding Top 3 Cities by Spend ---")
start_time_top_cities = time.time()
top_cities_by_spend = transactions_with_date.groupBy("city") \
    .agg({"amt": "sum"}) \
    .withColumnRenamed("sum(amt)", "total_transaction_amount") \
    .orderBy(col("total_transaction_amount").desc()) \
    .limit(3)
top_cities_by_spend.show()
end_time_top_cities = time.time()
print(f"Time taken for 'Top 3 Cities' analysis: {end_time_top_cities - start_time_top_cities:.2f} seconds")    #4.14 sec

#To observe the Spark UI while the application is running, use sleep() command
time.sleep(300)
# Stop Spark Session
spark.stop()
