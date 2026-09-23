import feedparser

def get_trending_topics(subreddit="india", limit=10):
    """Fetch hot posts from a subreddit via RSS (no API key needed)."""
    url = f"https://www.reddit.com/r/{subreddit}/hot/.rss"
    feed = feedparser.parse(url)
    
    topics = []
    for entry in feed.entries[:limit]:
        topics.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "")
        })
    return topics


if __name__ == "__main__":
    topics = get_trending_topics()
    for i, t in enumerate(topics, 1):
        print(f"{i}. {t['title']}")
