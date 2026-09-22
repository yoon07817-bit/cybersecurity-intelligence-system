from datetime import datetime
from zoneinfo import ZoneInfo

import feedparser
import requests

from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from config import RSS_FEEDS


# ==========================================================
# DATE FORMATTING
# ==========================================================

def format_date(date_string):
    """
    Convert RSS publication date into Myanmar Time
    (MMT / UTC+6:30).
    """

    try:

        if date_string:

            parsed_date = datetime.strptime(
                date_string,
                "%a, %d %b %Y %H:%M:%S %z"
            )

            myanmar_time = parsed_date.astimezone(
                ZoneInfo("Asia/Yangon")
            )

            return myanmar_time.strftime(
                "%Y-%m-%d %H:%M:%S MMT"
            )

    except Exception:
        pass


    # Fallback if RSS date cannot be parsed

    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )


# ==========================================================
# RSS FETCHING
# ==========================================================

def fetch_articles():
    """
    Fetch articles from all configured RSS feeds.

    This function is responsible only for collecting
    RSS metadata.

    Final category and severity classification are handled
    later by scorer.py.

    Therefore, this function does NOT assign a security
    category based on keywords.
    """

    articles = []


    # ======================================================
    # HTTP SESSION
    # ======================================================

    session = requests.Session()


    retries = Retry(

        total=3,

        backoff_factor=1,

        status_forcelist=[
            500,
            502,
            503,
            504
        ],

        raise_on_status=False

    )


    adapter = HTTPAdapter(
        max_retries=retries
    )


    session.mount(
        "https://",
        adapter
    )


    session.mount(
        "http://",
        adapter
    )


    # ======================================================
    # REQUEST HEADERS
    # ======================================================

    headers = {

        "User-Agent":
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/122.0.0.0 "
            "Safari/537.36",

        "Accept":
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,image/webp,"
            "*/*;q=0.8",

        "Accept-Language":
            "en-US,en;q=0.5",

        "Referer":
            "https://www.google.com/"

    }


    # ======================================================
    # FETCH EACH RSS SOURCE
    # ======================================================

    for feed in RSS_FEEDS:

        source = feed.get(
            "source",
            "Unknown Source"
        )


        feed_url = feed.get(
            "url",
            ""
        )


        print(
            f"Fetching: {source}"
        )


        try:

            response = session.get(

                feed_url,

                headers=headers,

                timeout=(10, 25)

            )


            # ------------------------------------------------
            # HTTP ERROR
            # ------------------------------------------------

            if response.status_code != 200:

                print(

                    f"Skipping {source}: "
                    f"Received HTTP status code "
                    f"{response.status_code}"

                )

                continue


            # ------------------------------------------------
            # PARSE RSS
            # ------------------------------------------------

            rss = feedparser.parse(
                response.content
            )


        except requests.RequestException as e:

            print(

                f"Failed to fetch {source}: "
                f"{e}"

            )

            continue


        except Exception as e:

            print(

                f"Failed to parse {source}: "
                f"{e}"

            )

            continue


        # ==================================================
        # PROCESS RSS ENTRIES
        # ==================================================

        for entry in rss.entries:

            try:

                title = (
                    entry.get(
                        "title",
                        ""
                    )
                    or ""
                ).strip()


                url = (
                    entry.get(
                        "link",
                        ""
                    )
                    or ""
                ).strip()


                published = (
                    entry.get(
                        "published",
                        ""
                    )
                    or ""
                )


                # ------------------------------------------------
                # Ignore completely empty RSS entries
                # ------------------------------------------------

                if not title and not url:

                    continue


                # ------------------------------------------------
                # RSS DESCRIPTION
                # ------------------------------------------------

                description = (

                    entry.get(
                        "summary",
                        ""
                    )

                    or

                    entry.get(
                        "description",
                        ""
                    )

                    or

                    ""

                )


                # ------------------------------------------------
                # Store RSS metadata
                # ------------------------------------------------

                article = {

                    "title":
                        title,

                    "url":
                        url,

                    "published_date":
                        format_date(
                            published
                        ),

                    "source":
                        source,

                    # Keep RSS description available
                    # for main.py as a fallback.

                    "description":
                        description,

                }


                articles.append(
                    article
                )


            except Exception as e:

                print(

                    f"Failed to process RSS entry "
                    f"from {source}: {e}"

                )


    return articles


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == "__main__":

    articles = fetch_articles()


    print(
        f"\nTotal Articles: {len(articles)}\n"
    )


    # ------------------------------------------------------
    # Count articles by source
    # ------------------------------------------------------

    source_count = {}


    shown = 0


    for article in articles:

        source = article.get(
            "source",
            "Unknown"
        )


        if source_count.get(
            source,
            0
        ) < 2:

            print(
                "-" * 60
            )


            print(
                "Title:",
                article.get(
                    "title",
                    ""
                )
            )


            print(
                "Source:",
                article.get(
                    "source",
                    ""
                )
            )


            print(
                "Date:",
                article.get(
                    "published_date",
                    ""
                )
            )


            print(
                "URL:",
                article.get(
                    "url",
                    ""
                )
            )


            # Show whether RSS description exists

            description = article.get(
                "description",
                ""
            )


            if description:

                print(
                    "RSS Description: Available"
                )

            else:

                print(
                    "RSS Description: Not available"
                )


            source_count[source] = (
                source_count.get(
                    source,
                    0
                ) + 1
            )


            shown += 1


        if shown == 10:

            break