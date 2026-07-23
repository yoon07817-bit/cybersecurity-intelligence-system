from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


MYANMAR_TZ = ZoneInfo("Asia/Yangon")


def filter_recent_articles(articles):
    """
    Keep only articles published in the last 24 hours.
    """

    filtered_articles = []


    # Current Myanmar time - 24 hours
    cutoff = datetime.now(MYANMAR_TZ) - timedelta(hours=24)


    for article in articles:


        # Skip articles without date
        if not article.get("published_date"):
            continue


        try:

            # Convert fetcher.py date format:
            # 2026-07-23 18:45:00 MMT

            article_date = datetime.strptime(
                article["published_date"],
                "%Y-%m-%d %H:%M:%S MMT"
            )


            # Add Myanmar timezone information

            article_date = article_date.replace(
                tzinfo=MYANMAR_TZ
            )


            # Keep only last 24 hours articles

            if article_date > cutoff:
                filtered_articles.append(article)


        except Exception as e:

            print(
                "Date parsing failed:",
                article["published_date"]
            )

            print(e)

            continue


    return filtered_articles



def remove_duplicates(articles):
    """
    Remove duplicate articles based on:
    1. Same URL
    2. Same title
    """


    unique_articles = []


    seen_urls = set()

    seen_titles = set()



    for article in articles:


        url = article.get("url", "")

        title = article.get("title", "")



        # Duplicate URL

        if url in seen_urls:
            continue



        # Duplicate title

        if title in seen_titles:
            continue



        # Keep article

        unique_articles.append(article)



        # Remember

        seen_urls.add(url)

        seen_titles.add(title)



    return unique_articles