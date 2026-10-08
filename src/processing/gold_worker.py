import os
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, count, max as spark_max, to_date, desc, row_number
)
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    col, count, max as spark_max, to_date, desc, row_number, from_unixtime, countDistinct
)


SILVER_PATH = os.path.abspath("delta/silver/memes")
GOLD_SOURCE_PATH = os.path.abspath("delta/gold/source_stats")
GOLD_DAILY_PATH = os.path.abspath("delta/gold/daily_stats")


def create_spark_session():
    builder = (SparkSession.builder
        .appName("TrendPulse-Gold")
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0")
        .config("spark.sql.shuffle.partitions", "4")
        .master("local[*]"))
    return builder.getOrCreate()


from pyspark.sql.functions import from_unixtime, date_format

def build_source_stats(spark, silver_df):
    silver = silver_df.withColumn("date", to_date(from_unixtime(col("processed_at"))))

    w = Window.partitionBy("source").orderBy(desc("processed_at"))

    latest_per_source = (silver
        .withColumn("rn", row_number().over(w))
        .filter(col("rn") == 1)
        .select(
            col("source"),
            col("meme").alias("latest_meme"),
            col("emoji").alias("latest_emoji"),
            from_unixtime(col("processed_at")).alias("latest_timestamp")   # ← convert here
        ))

    counts = silver.groupBy("source").agg(count("*").alias("total_memes"))

    return counts.join(latest_per_source, on="source")


def build_daily_stats(spark, silver_df):
    """Aggregate per day: count, sources active, top source."""
    silver = silver_df.withColumn(
        "date",
        to_date(from_unixtime(col("processed_at")))
    )

    # Count per day + source
    daily_source = (silver
        .groupBy("date", "source")
        .agg(count("*").alias("cnt")))

    # Total per day + distinct sources
    daily_total = (silver
        .groupBy("date")
        .agg(
            count("*").alias("total_memes"),
            countDistinct("source").alias("sources_active")
        ))

    # Top source per day (highest count)
    w = Window.partitionBy("date").orderBy(desc("cnt"))
    top_source = (daily_source
        .withColumn("rn", row_number().over(w))
        .filter(col("rn") == 1)
        .select("date", col("source").alias("top_source")))

    return daily_total.join(top_source, on="date")

def run_gold():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    try:
        silver_df = spark.read.format("delta").load(SILVER_PATH)
    except Exception:
        print("No silver data found. Run silver_worker first.")
        spark.stop()
        return

    if silver_df.count() == 0:
        print("Silver is empty. Nothing to aggregate.")
        spark.stop()
        return

    # ---------- Source stats ----------
    print("Building source_stats...")
    source_stats = build_source_stats(spark, silver_df).orderBy(desc("total_memes"))

    (source_stats.write
        .format("delta")
        .mode("overwrite")
        .save(GOLD_SOURCE_PATH))

    print(f"  Wrote {source_stats.count()} rows to source_stats")
    source_stats.show(truncate=False)

    # ---------- Daily stats ----------
    print("\nBuilding daily_stats...")
    daily_stats = build_daily_stats(spark, silver_df).orderBy(desc("date"))

    (daily_stats.write
        .format("delta")
        .mode("overwrite")
        .save(GOLD_DAILY_PATH))

    print(f"  Wrote {daily_stats.count()} rows to daily_stats")
    daily_stats.show(truncate=False)

    spark.stop()
    print("\nGold complete.")


if __name__ == "__main__":
    run_gold()