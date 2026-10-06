# import json
# import time
# from kafka import KafkaProducer
# from src.ingestion.reddit_ingester import get_trending_topics


# KAFKA_BROKER = "localhost:9092"
# TOPIC = "reddit-trends"


# def create_producer():
#     """Create a Kafka producer that sends JSON messages."""
#     return KafkaProducer(
#         bootstrap_servers=KAFKA_BROKER,
#         value_serializer=lambda v: json.dumps(v).encode("utf-8"),
#         key_serializer=lambda k: k.encode("utf-8") if k else None,
#     )


# def stream_topics(subreddits=None, limit=5, interval=300):
#     """Stream from multiple subreddits in one cycle."""
#     if subreddits is None:
#         subreddits = ["india", "worldnews", "bengaluru", "cricket"]

#     producer = create_producer()
#     seen = set()

#     print(f"Producer connected to Kafka at {KAFKA_BROKER}")
#     print(f"Streaming to topic: {TOPIC}")
#     print(f"Subreddits: {', '.join(subreddits)}")
#     print(f"Fetching every {interval}s. Ctrl+C to stop.\n")

#     while True:
#         new_count = 0
#         for sub in subreddits:
#             topics = get_trending_topics(subreddit=sub, limit=limit)
#             for topic in topics:
#                 link = topic["link"]
#                 if link in seen:
#                     continue
#                 seen.add(link)

#                 message = {
#                     "title": topic["title"],
#                     "link": link,
#                     "subreddit": sub,
#                     "timestamp": time.time(),
#                 }
#                 producer.send(TOPIC, key=link, value=message)
#                 new_count += 1
#             time.sleep(3) # be nice to reddit
#         producer.flush()
#         print(f"  [pushed {new_count} new messages, sleeping {interval}s]\n")
#         time.sleep(interval)


# if __name__ == "__main__":
#     stream_topics(limit=5, interval=60)

import json
import time
from kafka import KafkaProducer
from src.ingestion.news_ingester import get_trending_topics


KAFKA_BROKER = "localhost:9092"
TOPIC = "trendpulse-sources"


def create_producer():
    """Create a Kafka producer that sends JSON messages."""
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )


def stream_topics(sources=None, limit=5, interval=300):
    """Stream from multiple news sources in one cycle."""
    if sources is None:
        sources = ["india", "worldnews", "bengaluru", "cricket"]

    producer = create_producer()
    seen = set()

    print(f"Producer connected to Kafka at {KAFKA_BROKER}")
    print(f"Streaming to topic: {TOPIC}")
    print(f"Sources: {', '.join(sources)}")
    print(f"Fetching every {interval}s. Ctrl+C to stop.\n")

    while True:
        new_count = 0
        for source in sources:
            topics = get_trending_topics(subreddit=source, limit=limit)
            for topic in topics:
                link = topic["link"]
                if link in seen:
                    continue
                seen.add(link)

                message = {
                    "title": topic["title"],
                    "link": link,
                    "source": source,
                    "timestamp": time.time(),
                }
                producer.send(TOPIC, key=link, value=message)
                new_count += 1
            time.sleep(3)  # polite delay between sources

        producer.flush()
        print(f"  [pushed {new_count} new messages, sleeping {interval}s]\n")
        time.sleep(interval)


if __name__ == "__main__":
    stream_topics(limit=5, interval=60)