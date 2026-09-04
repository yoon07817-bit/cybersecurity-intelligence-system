import logging
import sys
from colorama import init, Fore, Style

from fetcher import fetch_articles
from filter import filter_recent_articles, remove_duplicates
from database import create_table, save_article, article_exists
from extractor import extract_article
from summariser import summarize
from scorer import score_article

# Initialize terminal color output
init()

# Configure logging for pipeline operational events
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)


def print_colored_summary(summary: str):
    """
    Prints AI-generated article summary to console with color coding.
    """
    for line in summary.split("\n"):
        if "Main Point" in line:
            print(Fore.CYAN + line + Style.RESET_ALL)
        elif "Key Points" in line:
            print(Fore.YELLOW + line + Style.RESET_ALL)
        elif "Summary" in line:
            print(Fore.MAGENTA + line + Style.RESET_ALL)
        elif line.startswith("-"):
            print(Fore.GREEN + line + Style.RESET_ALL)
        else:
            print(Fore.WHITE + line + Style.RESET_ALL)


def print_threat_score_breakdown(article: dict):
    """
    Displays detailed breakdown of keyword hits and final threat scores.
    """
    print("\nTHREAT SCORE BREAKDOWN")
    print("-" * 50)

    # Critical Severity Keywords
    print("\nCritical Keywords (5 points each):")
    if article.get("critical_keywords"):
        for keyword in article["critical_keywords"]:
            print(f"- {keyword}")
        critical_score = len(article["critical_keywords"]) * 5
    else:
        print("None")
        critical_score = 0
    print(f"Contribution: {critical_score}")

    # High Severity Keywords
    print("\nHigh Keywords (3 points each):")
    if article.get("high_keywords"):
        for keyword in article["high_keywords"]:
            print(f"- {keyword}")
        high_score = len(article["high_keywords"]) * 3
    else:
        print("None")
        high_score = 0
    print(f"Contribution: {high_score}")

    # Medium Severity Keywords
    print("\nMedium Keywords (1 point each):")
    if article.get("medium_keywords"):
        for keyword in article["medium_keywords"]:
            print(f"- {keyword}")
        medium_score = len(article["medium_keywords"]) * 1
    else:
        print("None")
        medium_score = 0
    print(f"Contribution: {medium_score}")

    print("\n" + "-" * 50)
    print(f"TOTAL SCORE: {article.get('score', 0)}")
    print(f"FINAL SEVERITY: {article.get('severity', 'Low')}")


def main():
    # Step 0: Ensure database and schema exist
    create_table()

    # Step 1: Fetch Articles from configured RSS feeds
    logging.info("Fetching articles from sources...")
    articles = fetch_articles()
    total_fetched = len(articles)

    print("\nPIPELINE PROCESSING")
    print("-" * 50)
    print(f"Total fetched articles: {total_fetched}")

    # Step 2: Filter by recency (e.g., past 24 hours)
    recent_articles = filter_recent_articles(articles)
    print(f"Articles after 24-hour filtering: {len(recent_articles)}")

    # Step 3: Remove duplicate articles by URL/Title
    unique_articles = remove_duplicates(recent_articles)
    print(f"Articles after duplicate removal: {len(unique_articles)}")

    duplicates_removed = len(recent_articles) - len(unique_articles)
    new_articles = len(unique_articles)

    print("\nSUMMARY")
    print("-" * 50)
    print(f"{total_fetched} articles fetched, {duplicates_removed} duplicates removed, {new_articles} unique recent articles.")

    print("\nFINAL ARTICLES")
    print("-" * 50)
    print("\nUnique articles by source:")
    
    counts = {}
    for article in unique_articles:
        counts[article["source"]] = counts.get(article["source"], 0) + 1

    for source, count in counts.items():
        print(f" - {source}: {count}")

    # Select top balanced articles across sources (up to 10 total)
    selected_articles = []
    source_count = {}

    for article in unique_articles:
        source = article["source"]
        if source_count.get(source, 0) < 3:  # Max 3 per source for diversity
            selected_articles.append(article)
            source_count[source] = source_count.get(source, 0) + 1

    # Cap processing list to top 10
    selected_articles = selected_articles[:10]
    total_articles = len(selected_articles)

    for index, article in enumerate(selected_articles, start=1):
        print(f"\n[{index}/{total_articles}] Processing article...")

        if article_exists(article["url"]):
            print(f"Skipping article already in database: {article['title']}")
            continue

        print("\n========================================")
        print("Title:", article["title"])

        try:
            # Step 4: Full-text extraction
            print("\nExtracting article content...")
            article_text = extract_article(article["url"])

            if article_text:
                article["content"] = article_text
                print("Article extracted successfully.")
                print("Generating summary with Groq AI...")
                article["summary"] = summarize(article["title"], article_text)
            else:
                article["content"] = ""
                print("No article body found. Summarising title only.")
                article["summary"] = summarize(article["title"], article["title"])

            # Step 5: Score article severity and keywords
            result = score_article(article["title"], article["summary"])

            article["severity"] = result.get("severity", "Low")
            article["score"] = result.get("score", 0)
            article["critical_keywords"] = result.get("critical_keywords", [])
            article["high_keywords"] = result.get("high_keywords", [])
            article["medium_keywords"] = result.get("medium_keywords", [])

            # Step 6: Save parsed article to database
            save_article(article)

            # Output processed info
            print("\nSAVED ARTICLE TO DATABASE")
            print("-" * 50)
            print("Title   :", article["title"])
            print("Source  :", article["source"])
            print("Category:", article.get("category", "Uncategorized"))
            print("Date    :", article.get("published_date", "N/A"))
            print("URL     :", article["url"])

            print("\nSUMMARY")
            print("-" * 50)
            print_colored_summary(article["summary"])

            # Threat score breakdown
            print_threat_score_breakdown(article)

        except Exception as e:
            logging.error(f"Error processing article '{article.get('title')}': {e}", exc_info=True)
            continue

    print("\nPipeline execution completed successfully.")


if __name__ == "__main__":
    main()