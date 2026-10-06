import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType
from delta import configure_spark_with_delta_pip


# ---------- Config ----------
KAFKA_BROKER = "localhost:9092"
TOPIC = "trendpulse-sources"
BRONZE_PATH = os.path.abspath("delta/bronze/memes")
CHECKPOINT_PATH = os.path.abspath("delta/checkpoints/bronze")


# ---------- Kafka message schema ----------
MESSAGE_SCHEMA = StructType() \
    .add("title", StringType()) \
    .add("link", StringType()) \
    .add("source", StringType()) \
    .add("timestamp", DoubleType())

def create_spark_session():
    """Create Spark session with Delta + Kafka support."""
    builder = (SparkSession.builder
        .appName("TrendPulse-Bronze")
        .config("spark.sql.extensions",
                "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.jars.packages",
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3,"
                "io.delta:delta-spark_2.12:3.2.0")
        .config("spark.sql.shuffle.partitions", "4")
        .master("local[*]"))
    return builder.getOrCreate()


def run_bronze_stream():
    """Stream from Kafka, write raw data to Delta bronze layer."""
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print(f"Reading from Kafka: {KAFKA_BROKER} / topic: {TOPIC}")
    print(f"Writing to Bronze: {BRONZE_PATH}")
    print(f"Checkpoint: {CHECKPOINT_PATH}\n")

    # Read stream from Kafka
    kafka_df = (spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BROKER)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load())

    # Kafka value is bytes → parse JSON
    parsed_df = (kafka_df
        .selectExpr("CAST(value AS STRING) as json_str")
        .select(from_json(col("json_str"), MESSAGE_SCHEMA).alias("data"))
        .select("data.*"))

    # Write to Delta (bronze = raw, append-only)
    query = (parsed_df.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", CHECKPOINT_PATH)
        .start(BRONZE_PATH))

    print("Stream started. Waiting for data...")
    print("Press Ctrl+C to stop.\n")

    query.awaitTermination()


if __name__ == "__main__":
    run_bronze_stream()