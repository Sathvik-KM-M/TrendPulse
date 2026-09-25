from src.ingestion.reddit_ingester import get_trending_topics
from src.llm.meme_generator import generate_caption


def run_pipeline(subreddit: str = "india", limit: int = 5):
    """Fetch Reddit trends and generate memes for each."""
    print(f"Fetching trending topics from r/{subreddit}...\n")
    topics = get_trending_topics(subreddit=subreddit, limit=limit)

    results = []
    for i, topic in enumerate(topics, 1):
        title = topic["title"]
        print(f"[{i}/{limit}] {title}")

        caption = generate_caption(title)
        print(f"  → Meme: {caption}\n")

        results.append({
            "topic": title,
            "link": topic["link"],
            "meme": caption,
        })

    return results


if __name__ == "__main__":
    run_pipeline(subreddit="india", limit=5)
