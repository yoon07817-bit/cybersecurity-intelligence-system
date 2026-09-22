import logging
import sys

from colorama import init, Fore, Style

from fetcher import fetch_articles
from filter import filter_recent_articles, remove_duplicates

from database import (
    create_table,
    save_article,
    article_exists,
    get_recommendation
)

from extractor import extract_article
from summariser import summarize
from scorer import score_article


# ==========================================================
# INITIALIZE TERMINAL COLOUR OUTPUT
# ==========================================================

init()


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)


# ==========================================================
# PRINT COLOURED SUMMARY
# ==========================================================

def print_colored_summary(summary: str):
    """
    Print the AI-generated article summary
    with simple terminal colour coding.
    """

    if not summary:

        print(
            Fore.WHITE
            + "No summary available."
            + Style.RESET_ALL
        )

        return


    for line in summary.split("\n"):

        if "Main Point" in line:

            print(
                Fore.CYAN
                + line
                + Style.RESET_ALL
            )

        elif "Key Points" in line:

            print(
                Fore.YELLOW
                + line
                + Style.RESET_ALL
            )

        elif "Summary" in line:

            print(
                Fore.MAGENTA
                + line
                + Style.RESET_ALL
            )

        elif line.startswith("-"):

            print(
                Fore.GREEN
                + line
                + Style.RESET_ALL
            )

        else:

            print(
                Fore.WHITE
                + line
                + Style.RESET_ALL
            )


# ==========================================================
# THREAT SCORE BREAKDOWN
# ==========================================================

def print_threat_score_breakdown(article: dict):
    """
    Display detailed breakdown of keyword hits
    and final threat score.
    """

    print(
        "\nTHREAT SCORE BREAKDOWN"
    )

    print(
        "-" * 50
    )


    # ------------------------------------------------------
    # Critical Keywords
    # ------------------------------------------------------

    print(
        "\nCritical Keywords (5 points each):"
    )


    if article.get("critical_keywords"):

        for keyword in article["critical_keywords"]:

            print(
                f"- {keyword}"
            )


        critical_score = (
            len(
                article["critical_keywords"]
            ) * 5
        )

    else:

        print("None")

        critical_score = 0


    print(
        f"Contribution: {critical_score}"
    )


    # ------------------------------------------------------
    # High Keywords
    # ------------------------------------------------------

    print(
        "\nHigh Keywords (3 points each):"
    )


    if article.get("high_keywords"):

        for keyword in article["high_keywords"]:

            print(
                f"- {keyword}"
            )


        high_score = (
            len(
                article["high_keywords"]
            ) * 3
        )

    else:

        print("None")

        high_score = 0


    print(
        f"Contribution: {high_score}"
    )


    # ------------------------------------------------------
    # Medium Keywords
    # ------------------------------------------------------

    print(
        "\nMedium Keywords (1 point each):"
    )


    if article.get("medium_keywords"):

        for keyword in article["medium_keywords"]:

            print(
                f"- {keyword}"
            )


        medium_score = len(
            article["medium_keywords"]
        )

    else:

        print("None")

        medium_score = 0


    print(
        f"Contribution: {medium_score}"
    )


    # ------------------------------------------------------
    # Final Score
    # ------------------------------------------------------

    print(
        "\n" + "-" * 50
    )


    print(
        f"TOTAL SCORE: "
        f"{article.get('score', 0)}"
    )


    print(
        f"FINAL SEVERITY: "
        f"{article.get('severity', 'Low')}"
    )


# ==========================================================
# PROTECTION RECOMMENDATION
# ==========================================================

def get_article_recommendation(article: dict):
    """
    Get a protection recommendation based on
    article category and severity.
    """

    category = article.get(
        "category",
        "General Security"
    )


    severity = article.get(
        "severity",
        "Low"
    )


    try:

        recommendation = get_recommendation(
            category,
            severity
        )

    except Exception as e:

        logging.error(
            f"Recommendation lookup failed: {e}"
        )

        recommendation = None


    # ------------------------------------------------------
    # Fallback recommendation
    # ------------------------------------------------------

    if not recommendation:

        recommendation = (
            "Maintain regular security updates, "
            "monitor security threats, review access "
            "controls, and follow appropriate "
            "cybersecurity best practices."
        )


    return recommendation


# ==========================================================
# PRINT PROTECTION RECOMMENDATION
# ==========================================================

def print_protection_recommendation(article: dict):
    """
    Display and store the protection recommendation
    in the article dictionary.
    """

    category = article.get(
        "category",
        "General Security"
    )


    severity = article.get(
        "severity",
        "Low"
    )


    recommendation = (
        get_article_recommendation(
            article
        )
    )


    # Store recommendation so that it can be
    # used by the dashboard/email system.

    article["recommendation"] = (
        recommendation
    )


    print(
        "\nPROTECTION RECOMMENDATION"
    )


    print(
        "-" * 50
    )


    print(
        f"Category : {category}"
    )


    print(
        f"Severity : {severity}"
    )


    print(
        "\nAdvice:"
    )


    print(
        recommendation
    )


    return recommendation


# ==========================================================
# CVE DETECTION
# ==========================================================

def detect_article_cves(article: dict):
    """
    Detect CVE identifiers from the article title,
    summary and extracted article content.

    Articles without CVEs are processed normally.
    """

    try:

        from cve_detector import extract_cves

    except ImportError:

        logging.warning(
            "cve_detector.py could not be imported."
        )

        return []


    title = article.get(
        "title",
        ""
    )


    summary = article.get(
        "summary",
        ""
    )


    content = article.get(
        "content",
        ""
    )


    combined_text = (
        f"{title}\n"
        f"{summary}\n"
        f"{content}"
    )


    try:

        detected = extract_cves(
            combined_text
        )

    except Exception as e:

        logging.warning(
            f"CVE detection failed: {e}"
        )

        return []


    if not detected:

        return []


    # ------------------------------------------------------
    # Remove duplicate CVE IDs
    # ------------------------------------------------------

    unique_cves = []

    seen = set()


    for cve in detected:

        cve = str(
            cve
        ).upper().strip()


        if cve not in seen:

            seen.add(
                cve
            )

            unique_cves.append(
                cve
            )


    return unique_cves


# ==========================================================
# ARTICLE CONTENT + SUMMARY
# ==========================================================

def prepare_article_content(article: dict):
    """
    Prepare the best available article content.

    Priority:

    1. Full webpage article extraction
    2. RSS description
    3. Article title

    This prevents a failed webpage extraction from
    automatically losing the RSS information.
    """

    title = article.get(
        "title",
        ""
    )


    rss_description = article.get(
        "description",
        ""
    )


    # ------------------------------------------------------
    # STEP 1 — Try webpage extraction
    # ------------------------------------------------------

    print(
        "\nExtracting article content..."
    )


    try:

        article_text = extract_article(
            article.get(
                "url",
                ""
            )
        )

    except Exception as e:

        logging.warning(
            f"Article extraction failed: {e}"
        )

        article_text = None


    # ------------------------------------------------------
    # Full article successfully extracted
    # ------------------------------------------------------

    if article_text:

        article_text = str(
            article_text
        ).strip()


    if article_text:

        article["content"] = (
            article_text
        )


        article["content_source"] = (
            "Web Article"
        )


        print(
            "Article extracted successfully."
        )


        print(
            "Content source: Web Article"
        )


        print(
            "Generating summary with Groq AI..."
        )


        try:

            summary = summarize(
                title,
                article_text
            )

        except Exception as e:

            logging.warning(
                f"Groq summarisation failed: {e}"
            )

            summary = None


        if summary:

            article["summary"] = (
                summary
            )

        else:

            # Safe fallback if Groq returns
            # an empty response.

            article["summary"] = (
                article_text[:3000]
            )


        return


    # ------------------------------------------------------
    # STEP 2 — Web extraction failed
    # Use RSS description
    # ------------------------------------------------------

    print(
        "No article body extracted."
    )


    if rss_description:

        rss_description = str(
            rss_description
        ).strip()


        article["content"] = (
            rss_description
        )


        article["content_source"] = (
            "RSS Description"
        )


        print(
            "Using RSS description as fallback."
        )


        print(
            "Content source: RSS Description"
        )


        print(
            "Generating summary with Groq AI..."
        )


        try:

            summary = summarize(
                title,
                rss_description
            )

        except Exception as e:

            logging.warning(
                f"Groq summarisation failed: {e}"
            )

            summary = None


        if summary:

            article["summary"] = (
                summary
            )

        else:

            article["summary"] = (
                rss_description[:3000]
            )


        return


    # ------------------------------------------------------
    # STEP 3 — No webpage body and no RSS description
    # Use title only
    # ------------------------------------------------------

    article["content"] = ""

    article["content_source"] = (
        "RSS Title Only"
    )


    print(
        "No article body or RSS description found."
    )


    print(
        "Using title-only fallback."
    )


    # IMPORTANT:
    # Do not ask the AI to invent a summary from
    # a title when there is no article content.

    article["summary"] = (
        f"Article title: {title}. "
        "No article body or RSS description was "
        "available for further analysis."
    )


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def main():

    # ======================================================
    # STEP 0 — ENSURE DATABASE EXISTS
    # ======================================================

    create_table()


    # ======================================================
    # STEP 1 — FETCH ARTICLES
    # ======================================================

    logging.info(
        "Fetching articles from sources..."
    )


    articles = fetch_articles()


    total_fetched = len(
        articles
    )


    print(
        "\nPIPELINE PROCESSING"
    )


    print(
        "-" * 50
    )


    print(
        f"Total fetched articles: "
        f"{total_fetched}"
    )


    # ======================================================
    # STEP 2 — FILTER RECENT ARTICLES
    # ======================================================

    recent_articles = (
        filter_recent_articles(
            articles
        )
    )


    print(
        "Articles after 24-hour filtering: "
        f"{len(recent_articles)}"
    )


    # ======================================================
    # STEP 3 — REMOVE DUPLICATES
    # ======================================================

    unique_articles = (
        remove_duplicates(
            recent_articles
        )
    )


    print(
        "Articles after duplicate removal: "
        f"{len(unique_articles)}"
    )


    duplicates_removed = (
        len(recent_articles)
        - len(unique_articles)
    )


    new_articles = len(
        unique_articles
    )


    print(
        "\nSUMMARY"
    )


    print(
        "-" * 50
    )


    print(
        f"{len(articles)} articles fetched, "
        f"{duplicates_removed} duplicates removed, "
        f"{new_articles} unique articles."
    )


    # ======================================================
    # STEP 4 — SOURCE DISTRIBUTION
    # ======================================================

    print(
        "\nFINAL ARTICLES"
    )


    print(
        "-" * 50
    )


    print(
        "\nUnique articles by source:"
    )


    counts = {}


    for article in unique_articles:

        source = article.get(
            "source",
            "Unknown"
        )


        counts[source] = (
            counts.get(
                source,
                0
            ) + 1
        )


    for source, count in counts.items():

        print(
            f" - {source}: {count}"
        )


    # ======================================================
    # STEP 5 — BALANCED ARTICLE SELECTION
    # ======================================================

    selected_articles = []

    source_count = {}


    for article in unique_articles:

        source = article.get(
            "source",
            "Unknown"
        )


        # Maximum 3 articles from each source

        if source_count.get(
            source,
            0
        ) < 3:

            selected_articles.append(
                article
            )


            source_count[source] = (
                source_count.get(
                    source,
                    0
                ) + 1
            )


    # ======================================================
    # KEEP YOUR EXISTING 10-ARTICLE LIMIT
    # ======================================================

    selected_articles = (
        selected_articles[:10]
    )


    total_articles = len(
        selected_articles
    )


    print(
        f"\nSelected {total_articles} "
        "articles for processing."
    )


    # ======================================================
    # STEP 6 — PROCESS SELECTED ARTICLES
    # ======================================================

    for index, article in enumerate(
        selected_articles,
        start=1
    ):


        print(
            f"\n[{index}/{total_articles}] "
            f"Processing article..."
        )


        # --------------------------------------------------
        # Check duplicate before expensive processing
        # --------------------------------------------------

        if article_exists(
            article["url"]
        ):

            print(
                "Skipping existing article: "
                f"{article['title']}"
            )

            continue


        print(
            "\n========================================"
        )


        print(
            "Title:",
            article["title"]
        )


        try:

            # ==================================================
            # STEP 7 — CONTENT EXTRACTION + SUMMARY
            # ==================================================

            prepare_article_content(
                article
            )


            # ==================================================
            # STEP 8 — CLASSIFY AND SCORE
            # ==================================================

            print(
                "\nAnalysing article category "
                "and threat severity..."
            )


            result = score_article(

                article["title"],

                article["summary"]

            )


            # --------------------------------------------------
            # Category
            # --------------------------------------------------

            article["category"] = (
                result.get(
                    "category",
                    "General Security"
                )
            )


            # --------------------------------------------------
            # Severity
            # --------------------------------------------------

            article["severity"] = (
                result.get(
                    "severity",
                    "Low"
                )
            )


            # --------------------------------------------------
            # Threat score
            # --------------------------------------------------

            article["score"] = (
                result.get(
                    "score",
                    0
                )
            )


            # --------------------------------------------------
            # Keyword information
            # --------------------------------------------------

            article["critical_keywords"] = (
                result.get(
                    "critical_keywords",
                    []
                )
            )


            article["high_keywords"] = (
                result.get(
                    "high_keywords",
                    []
                )
            )


            article["medium_keywords"] = (
                result.get(
                    "medium_keywords",
                    []
                )
            )


            # ==================================================
            # ARTICLE CLASSIFICATION
            # ==================================================

            print(
                "\nARTICLE CLASSIFICATION"
            )


            print(
                "-" * 50
            )


            print(
                "Category:",
                article["category"]
            )


            print(
                "Severity:",
                article["severity"]
            )


            print(
                "Score:",
                article["score"]
            )


            # ==================================================
            # STEP 9 — CVE DETECTION
            # ==================================================

            print(
                "\nCVE DETECTION"
            )


            print(
                "-" * 50
            )


            detected_cves = (
                detect_article_cves(
                    article
                )
            )


            article["cves"] = (
                detected_cves
            )


            if detected_cves:

                print(
                    "CVE(s) detected:"
                )


                for cve in detected_cves:

                    print(
                        f"- {cve}"
                    )


            else:

                print(
                    "No CVE detected."
                )


            # ==================================================
            # STEP 10 — PROTECTION RECOMMENDATION
            # ==================================================

            print_protection_recommendation(
                article
            )


            # ==================================================
            # STEP 11 — SAVE ARTICLE
            # ==================================================

            save_article(
                article
            )


            print(
                "\nSAVED ARTICLE TO DATABASE"
            )


            print(
                "-" * 50
            )


            print(
                "Title   :",
                article["title"]
            )


            print(
                "Source  :",
                article.get(
                    "source",
                    "Unknown"
                )
            )


            print(
                "Category:",
                article.get(
                    "category",
                    "General Security"
                )
            )


            print(
                "Severity:",
                article.get(
                    "severity",
                    "Low"
                )
            )


            print(
                "Score   :",
                article.get(
                    "score",
                    0
                )
            )


            print(
                "Date    :",
                article.get(
                    "published_date",
                    "N/A"
                )
            )


            print(
                "Content :",
                article.get(
                    "content_source",
                    "Unknown"
                )
            )


            print(
                "URL     :",
                article["url"]
            )


            # ==================================================
            # STEP 12 — DISPLAY SUMMARY
            # ==================================================

            print(
                "\nSUMMARY"
            )


            print(
                "-" * 50
            )


            print_colored_summary(
                article.get(
                    "summary",
                    ""
                )
            )


            # ==================================================
            # STEP 13 — THREAT SCORE BREAKDOWN
            # ==================================================

            print_threat_score_breakdown(
                article
            )


        except Exception as e:

            logging.error(

                "Error processing article "
                f"'{article.get('title', 'Unknown')}': "
                f"{e}",

                exc_info=True

            )

            continue


    # ======================================================
    # PIPELINE COMPLETE
    # ======================================================

    print(
        "\nPipeline execution completed successfully."
    )


# ==========================================================
# PROGRAM ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()