# import requests
# import feedparser

# HEADERS = {
#     "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
#                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
# }


# def get_trending_topics(subreddit="india", limit=10):
#     """Fetch hot posts from a subreddit via RSS."""
#     url = f"https://www.reddit.com/r/{subreddit}/hot/.rss"

#     try:
#         response = requests.get(url, headers=HEADERS, timeout=10)
#         response.raise_for_status()
#         feed = feedparser.parse(response.content)
#     except requests.RequestException as e:
#         print(f"[reddit_ingester] failed for r/{subreddit}: {e}")
#         return []

#     topics = []
#     for entry in feed.entries[:limit]:
#         topics.append({
#             "title": entry.title,
#             "link": entry.link,
#             "published": entry.get("published", "")
#         })
#     return topics
# Google
import requests
import feedparser

HEADERS = {
    "User-Agent": "TrendPulse/1.0 (portfolio project)"
}

SOURCE_URLS = {
    "india":     "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "worldnews": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-IN&gl=IN&ceid=IN:en",
    "bengaluru": "https://news.google.com/rss/search?q=bangalore&hl=en-IN&gl=IN&ceid=IN:en",
    "cricket":   "https://news.google.com/rss/search?q=cricket&hl=en-IN&gl=IN&ceid=IN:en",
}


def get_trending_topics(subreddit="india", limit=10):
    """Fetch items from a Google News RSS feed."""
    url = SOURCE_URLS.get(subreddit)
    if not url:
        print(f"[ingester] unknown source: {subreddit}")
        return []

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.RequestException as e:
        print(f"[ingester] failed for {subreddit}: {e}")
        return []

    topics = []
    for entry in feed.entries[:limit]:
        topics.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "")
        })
    return topics