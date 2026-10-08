import os
from pyspark.sql import SparkSession
from src.llm.meme_generator import generate_caption
import time


BRONZE_PATH = os.path.abspath("delta/bronze/memes")
SILVER_PATH = os.path.abspath("delta/silver/memes")


def create_spark_session():
    builder = (SparkSession.builder
        .appName("TrendPulse-Silver")
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.2.0")
        .config("spark.sql.shuffle.partitions", "4")
        .master("local[*]"))
    return builder.getOrCreate()


def get_bronze(spark):
    try:
        return spark.read.format("delta").load(BRONZE_PATH)
    except Exception:
        return None


def get_silver(spark):
    try:
        return spark.read.format("delta").load(SILVER_PATH)
    except Exception:
        return None


def get_new_rows(spark):
    """Return rows in bronze not yet in silver (as iterator)."""
    bronze = get_bronze(spark)
    if bronze is None or bronze.count() == 0:
        return None

    silver = get_silver(spark)

    if silver is not None:
        silver_links = silver.select("link").distinct()
        new_df = bronze.join(silver_links, on="link", how="left_anti")
    else:
        new_df = bronze

    new_df = new_df.dropDuplicates(["link"])

    # For full batch, change .limit(5) to no limit
    return new_df.toLocalIterator()


def run_silver():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("ERROR")

    new_rows_iter = get_new_rows(spark)
    if new_rows_iter is None:
        print("No bronze data found.")
        spark.stop()
        return

    processed = []
    count = 0

    print("Processing rows...\n")

    for row in new_rows_iter:
        count += 1
        title = row["title"]
        link = row["link"]
        source = row["source"]

        print(f"[{count}] {title[:60]}")
        try:
            result = generate_caption(title)
            meme = result.get("caption", "")
            emoji = result.get("emoji", "😂")
            #print(f"  → {emoji} {meme}")
        except Exception as e:
            print(f"  failed: {e}")
            meme = ""
            emoji = "😐"

        processed.append({
            "link": link,
            "topic": title,
            "source": source,
            "meme": meme,
            "emoji": emoji,
            "processed_at": time.time(),
        })

    if count == 0:
        print("Nothing new to process.")
        spark.stop()
        return

    print(f"\nProcessed {count} rows. Writing to silver...")

    df = spark.createDataFrame(processed)

    if get_silver(spark) is None:
        df.write.format("delta").mode("overwrite").save(SILVER_PATH)
    else:
        df.write.format("delta").mode("append").save(SILVER_PATH)

    print(f"Wrote {count} rows to silver.")
    spark.stop()


if __name__ == "__main__":
    run_silver()