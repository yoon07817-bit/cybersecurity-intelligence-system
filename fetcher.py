from datetime import datetime
import re
from zoneinfo import ZoneInfo
import feedparser
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from config import RSS_FEEDS


def detect_category(title):
    """Automatically assign category based on article title using keyword matching.

    Uses regex word boundaries for short terms like 'ai' to prevent false
    positives (e.g., 'email', 'chain').
    """
    title_lower = title.lower()

    if any(k in title_lower for k in ["ransomware", "malware", "trojan"]):
        return "Malware"

    if any(
        k in title_lower for k in ["cve-", "vulnerability", "flaw", "exploit"]
    ):
        return "Vulnerability"

    # Match exact word 'ai', or longer phrases
    if (
        re.search(r"\bai\b", title_lower)
        or "artificial intelligence" in title_lower
        or "machine learning" in title_lower
    ):
        return "AI Security"

    if any(k in title_lower for k in ["privacy", "data protection", "tracking"]):
        return "Privacy"

    if any(k in title_lower for k in ["cloud", "aws", "azure"]):
        return "Cloud Security"

    if any(k in title_lower for k in ["phishing", "scam"]):
        return "Phishing"

    if any(k in title_lower for k in ["zero-day", "0-day"]):
        return "Zero Day"

    if any(k in title_lower for k in ["linux", "windows", "macos"]):
        return "Operating Systems"

    if any(
        k in title_lower
        for k in ["password", "account", "authentication", "mfa"]
    ):
        return "Identity Security"

    if any(k in title_lower for k in ["github", "code", "developer"]):
        return "Application Security"

    return "General Security"


def format_date(date_string):
    """Convert RSS date into Myanmar Time (MMT / UTC+6:30)."""
    try:
        if date_string:
            parsed_date = datetime.strptime(
                date_string, "%a, %d %b %Y %H:%M:%S %z"
            )
            myanmar_time = parsed_date.astimezone(ZoneInfo("Asia/Yangon"))
            return myanmar_time.strftime("%Y-%m-%d %H:%M:%S MMT")
    except Exception:
        pass

    return datetime.now(ZoneInfo("Asia/Yangon")).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )


def fetch_articles():
    """Fetch articles from all RSS feed URLs using a resilient Session with automatic backoff retries."""
    articles = []

    # Configure session with automated retry and backoff strategy for stubborn feeds
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/"
    }

    for feed in RSS_FEEDS:
        print(f"Fetching: {feed['source']}")
        try:
            # Using a connection/read timeout tuple: (connect timeout, read timeout)
            response = session.get(feed["url"], headers=headers, timeout=(10, 25))
            
            if response.status_code != 200:
                print(f"Skipping {feed['source']}: Received HTTP status code {response.status_code}")
                continue
                
            rss = feedparser.parse(response.content)
        except Exception as e:
            print(f"Failed to fetch {feed['source']} due to network/firewall restriction. Skipping gracefully.")
            continue

        for entry in rss.entries:
            title = entry.get("title", "")

            article = {
                "title": title,
                "url": entry.get("link", ""),
                "published_date": format_date(entry.get("published", "")),
                "source": feed["source"],
                "category": detect_category(title),
            }

            articles.append(article)

    return articles


if __name__ == "__main__":
    articles = fetch_articles()

    print(f"\nTotal Articles: {len(articles)}\n")

    source_count = {}
    shown = 0

    for article in articles:
        source = article["source"]

        if source_count.get(source, 0) < 2:
            print("-" * 60)
            print("Title:", article["title"])
            print("Source:", article["source"])
            print("Category:", article["category"])
            print("Date:", article["published_date"])
            print("URL:", article["url"])

            source_count[source] = source_count.get(source, 0) + 1
            shown += 1

        if shown == 10:
            break