from fetcher import fetch_articles
from filter import (
    filter_recent_articles,
    remove_duplicates
)


def main():

    # Step 1: Fetch articles from RSS feeds
    articles = fetch_articles()

    # Duplicate list for testing duplicate removal
    # (This intentionally creates duplicate articles)
    articles = articles + articles

    # Count total fetched articles
    total_fetched = len(articles)

    print("\nPIPELINE PROCESSING")
    print("-" * 40)
    print("Total fetched articles:", total_fetched)

    # Step 2: Filter articles published in last 24 hours
    recent_articles = filter_recent_articles(articles)

    print("Articles after 24-hour filtering:",
          len(recent_articles))

    # Step 3: Remove duplicate articles
    unique_articles = remove_duplicates(recent_articles)

    print("Articles after duplicate removal:",
          len(unique_articles))

    # Calculate duplicates removed
    duplicates_removed = (
        len(recent_articles)
        - len(unique_articles)
    )

    # Final count of unique articles
    new_articles = len(unique_articles)

    # Step 4: Print summary
    print("\nSUMMARY")
    print("-" * 40)

    print(
        f"{total_fetched} articles fetched, "
        f"{duplicates_removed} duplicates removed, "
        f"{new_articles} new articles"
    )

    # Step 5: Show first 10 final articles
    print("\nFINAL ARTICLES")
    print("-" * 40)

    for article in unique_articles[:10]:

        print("\nTitle:", article["title"])
        print("Source:", article["source"])
        print("Date:", article["published_date"])
        print("URL:", article["url"])


if __name__ == "__main__":
    main()