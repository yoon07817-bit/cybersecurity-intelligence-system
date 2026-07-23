import feedparser
from datetime import datetime
from zoneinfo import ZoneInfo

from config import RSS_FEEDS


def detect_category(title):
    """
    Automatically assign category based on article title.
    """

    title = title.lower()

    if "ransomware" in title or "malware" in title or "trojan" in title:
        return "Malware"

    if "cve-" in title or "vulnerability" in title or "flaw" in title or "exploit" in title:
        return "Vulnerability"

    if "ai" in title or "artificial intelligence" in title or "machine learning" in title:
        return "AI Security"

    if "privacy" in title or "data protection" in title or "tracking" in title:
        return "Privacy"

    if "cloud" in title or "aws" in title or "azure" in title:
        return "Cloud Security"

    if "phishing" in title or "scam" in title:
        return "Phishing"

    if "zero-day" in title or "0-day" in title:
        return "Zero Day"

    if "linux" in title or "windows" in title or "macos" in title:
        return "Operating Systems"

    if "password" in title or "account" in title or "authentication" in title:
        return "Identity Security"

    if "github" in title or "code" in title or "developer" in title:
        return "Application Security"

    return "General Security"



def format_date(date_string):
    """
    Convert RSS date into Myanmar Time (MMT).
    """

    try:
        if date_string:

            # RSS date format
            parsed_date = datetime.strptime(
                date_string,
                "%a, %d %b %Y %H:%M:%S %z"
            )

            # Convert to Myanmar timezone
            myanmar_time = parsed_date.astimezone(
                ZoneInfo("Asia/Yangon")
            )

            return myanmar_time.strftime(
                "%Y-%m-%d %H:%M:%S MMT"
            )

    except Exception:
        pass


    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )



def fetch_articles():

    articles = []


    for feed in RSS_FEEDS:

        print(f"Fetching: {feed['source']}")


        rss = feedparser.parse(
            feed["url"]
        )


        for entry in rss.entries:

            title = entry.get(
                "title",
                ""
            )


            article = {

                "title": title,

                "url": entry.get(
                    "link",
                    ""
                ),

                "published_date": format_date(
                    entry.get(
                        "published",
                        ""
                    )
                ),

                "source": feed["source"],

                "category": detect_category(
                    title
                )
            }


            articles.append(article)


    return articles



if __name__ == "__main__":

    articles = fetch_articles()


    print(
        f"\nTotal Articles: {len(articles)}\n"
    )


    # Show 10 articles with different sources
    source_count = {}

    shown = 0


    for article in articles:

        source = article["source"]


        if source_count.get(source, 0) < 2:

            print("-" * 60)

            print(
                "Title:",
                article["title"]
            )

            print(
                "Source:",
                article["source"]
            )

            print(
                "Category:",
                article["category"]
            )

            print(
                "Date:",
                article["published_date"]
            )

            print(
                "URL:",
                article["url"]
            )


            source_count[source] = source_count.get(source, 0) + 1

            shown += 1


        if shown == 10:
            break