from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


def filter_recent_articles(articles):
    """
    Keep only articles published in last 24 hours
    """

    filtered_articles = []

    # current time minus 24 hours
    cutoff = datetime.now().astimezone() - timedelta(hours=24)

    for article in articles:

        # skip if article has no date
        if not article["published_date"]:
            continue

        try:
            # convert RSS date string to datetime object
            article_date = parsedate_to_datetime(
                article["published_date"]
            )

            # keep only recent articles
            if article_date > cutoff:
                filtered_articles.append(article)

        except Exception:
            # skip bad date format
            continue

    return filtered_articles


def remove_duplicates(articles):
    """
    Remove duplicate articles based on:
    1. same URL
    2. same exact title
    """

    unique_articles = []

    seen_urls = set()
    seen_titles = set()

    for article in articles:

        url = article["url"]
        title = article["title"]

        # duplicate URL
        if url in seen_urls:
            continue

        # duplicate title
        if title in seen_titles:
            continue

        # keep article
        unique_articles.append(article)

        # remember URL and title
        seen_urls.add(url)
        seen_titles.add(title)

    return unique_articles