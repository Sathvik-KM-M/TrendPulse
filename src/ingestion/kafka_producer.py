import json
import time
from kafka import KafkaProducer
from src.ingestion.reddit_ingester import get_trending_topics


# Kafka broker address (from your docker-compose setup)
KAFKA_BROKER = "localhost:9092"
TOPIC = "reddit-trends"


def create_producer():
    """Create a Kafka producer that sends JSON messages."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )


def stream_topics(subreddit: str = "india", limit: int = 5, interval: int = 300):
    """Fetch Reddit topics and push each to Kafka, forever."""
    producer = create_producer()
    print(f"Producer connected to Kafka at {KAFKA_BROKER}")
    print(f"Streaming to topic: {TOPIC}")
    print(f"Fetching r/{subreddit} every {interval}s. Ctrl+C to stop.\n")

    while True:
        topics = get_trending_topics(subreddit=subreddit, limit=limit)
        for topic in topics:
            message = {
                "title": topic["title"],
                "link": topic["link"],
                "subreddit": subreddit,
                "timestamp": time.time(),
            }
            producer.send(TOPIC, key=topic["link"], value=message)
            print(f"  → sent: {topic['title'][:60]}")

        producer.flush()
        print(f"  [pushed {len(topics)} messages, sleeping {interval}s]\n")
        time.sleep(interval)


if __name__ == "__main__":
    stream_topics(subreddit="india", limit=5, interval=300)