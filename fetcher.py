import feedparser
from config import RSS_FEEDS


def fetch_articles():
    articles = []

    for feed in RSS_FEEDS:
        print(f"Fetching: {feed['source']}")

        rss = feedparser.parse(feed["url"])

        for entry in rss.entries:

            article = {
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "published_date": entry.get("published", ""),
                "source": feed["source"],
                "category": feed["category"]
            }

            articles.append(article)

    return articles


if __name__ == "__main__":
    articles = fetch_articles()

    print(f"\nTotal Articles: {len(articles)}\n")

    for article in articles[:10]:
        print("-" * 60)
        print("Title:", article["title"])
        print("Source:", article["source"])
        print("Category:", article["category"])
        print("Date:", article["published_date"])
        print("URL:", article["url"])