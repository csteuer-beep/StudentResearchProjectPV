# main_month_agg.py
import uuid

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, mean, min, max

import mysql_module


# Main function to aggregate data
# Fetches raw data from MySQL, aggregates it and inserts the aggregated data back to MySQL
def main(month, year):
    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("Solarplant Data Aggregation") \
        .getOrCreate()

    # Fetch raw data
    raw_data = mysql_module.fetch_raw_data(month, year)
    if not raw_data:
        print("No data fetched")
        return

    # Convert raw data to Spark DataFrame
    df = spark.createDataFrame(raw_data)

    # List of unique Inst
    inst_list = df.select("Inst").distinct().collect()

    for inst_row in inst_list:
        inst = inst_row["Inst"]
        inst_df = df.filter(col("Inst") == inst)

        # Perform aggregations
        agg_df = inst_df.groupBy("Inst").agg(
            sum("P").alias("SumOfP"),
            mean("P").alias("MeanOfP"),
            min("P").alias("MinOfP"),
            max("P").alias("MaxOfP"),
            max("Tc").alias("MaxOfTc"),
            min("Tc").alias("MinOfTc"),
            mean("Tc").alias("MeanOfTc"),
            max("I").alias("MaxOfI"),
            min("I").alias("MinOfI"),
            mean("I").alias("MeanOfI"),
            max("V").alias("MaxOfV"),


            min("V").alias("MinOfV"),
            mean("V").alias("MeanOfV"),
            max("G").alias("MaxOfG"),
            min("G").alias("MinOfG"),
            mean("G").alias("MeanOfG")
        ).collect()[0]

        # Prepare data for insertion
        entry_id = str(uuid.uuid4())
        values = (
            entry_id, inst, year, month,
            agg_df["SumOfP"], agg_df["MeanOfP"], agg_df["MinOfP"], agg_df["MaxOfP"],
            agg_df["MaxOfTc"], agg_df["MinOfTc"], agg_df["MeanOfTc"],
            agg_df["MaxOfI"], agg_df["MinOfI"], agg_df["MeanOfI"],
            agg_df["MaxOfV"], agg_df["MinOfV"], agg_df["MeanOfV"],
            agg_df["MaxOfG"], agg_df["MinOfG"], agg_df["MeanOfG"]
        )

        # Insert aggregated data
        mysql_module.insert_aggregated_data(values)

    spark.stop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python main.py <month> <year>")
    else:
        month = int(sys.argv[1])
        year = int(sys.argv[2])
        main(month, year)
