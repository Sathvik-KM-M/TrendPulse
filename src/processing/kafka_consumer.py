import json
import time
import os
from kafka import KafkaConsumer
from src.llm.meme_generator import generate_caption


KAFKA_BROKER = "localhost:9092"
TOPIC = "reddit-trends"
GROUP_ID = "trendpulse-consumer-group"
OUTPUT_FILE = "data/memes.jsonl"


def create_consumer():
    """Create a Kafka consumer that reads JSON messages."""
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )


def save_meme(topic_title: str, link: str, subreddit: str, meme: str):
    """Append one meme to the output file."""
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    record = {
        "topic": topic_title,
        "link": link,
        "subreddit": subreddit,
        "meme": meme,
        "processed_at": time.time(),
    }
    with open(OUTPUT_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")


def run_consumer():
    """Read messages from Kafka, generate memes, save to file."""
    consumer = create_consumer()
    print(f"Consumer connected to Kafka at {KAFKA_BROKER}")
    print(f"Listening on topic: {TOPIC}")
    print(f"Saving memes to: {OUTPUT_FILE}")
    print("Ctrl+C to stop.\n")

    for message in consumer:
        data = message.value
        title = data["title"]
        link = data["link"]
        subreddit = data.get("subreddit", "unknown")

        print(f"[offset {message.offset}] {title[:60]}")
        meme = generate_caption(title)
        save_meme(title, link, subreddit, meme)
        print(f"  → meme: {meme}\n")


if __name__ == "__main__":
    run_consumer()