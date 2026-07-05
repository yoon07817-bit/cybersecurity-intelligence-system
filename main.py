from fetcher import fetch_articles
from filter import (
    filter_recent_articles,
    remove_duplicates
)

from database import create_table, save_article, article_exists

def main():

    # INIT DATABASE
    create_table()

    # STEP 1: FETCH ARTICLES
    articles = fetch_articles()

    # For testing duplicates
    articles = articles + articles

    total_fetched = len(articles)

    print("\nPIPELINE PROCESSING")
    print("-" * 40)
    print("Total fetched articles:", total_fetched)

    # STEP 2: FILTER (24 HOURS)
    recent_articles = filter_recent_articles(articles)

    print("Articles after 24-hour filtering:", len(recent_articles))

    # STEP 3: REMOVE DUPLICATES
    unique_articles = remove_duplicates(recent_articles)

    print("Articles after duplicate removal:", len(unique_articles))

    duplicates_removed = len(recent_articles) - len(unique_articles)
    new_articles = len(unique_articles)

    # SUMMARY
    print("\nSUMMARY")
    print("-" * 40)

    print(
        f"{total_fetched} articles fetched, "
        f"{duplicates_removed} duplicates removed, "
        f"{new_articles} new articles"
    )

    # STEP 4: FINAL PROCESSING + DATABASE SAVE
    print("\nFINAL ARTICLES")
    print("-" * 40)

    for article in unique_articles[:10]:

        # CHECK DATABASE FOR DUPLICATES
        if article_exists(article["url"]):
            print("Skipping duplicate:", article["title"])
            continue

        # SAFE DEFAULT FIELDS
        if "summary" not in article:
            article["summary"] = "No summary available"

        if "severity" not in article:
            article["severity"] = "Unknown"

        # SAVE TO DATABASE
        save_article(article)

        # OUTPUT
        print("\nSAVED ARTICLE")
        print("Title:", article["title"])
        print("Source:", article["source"])
        print("Date:", article["published_date"])
        print("URL:", article["url"])


# START PROGRAM
if __name__ == "__main__":
    main()