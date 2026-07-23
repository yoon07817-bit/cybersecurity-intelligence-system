from fetcher import fetch_articles

from filter import (
    filter_recent_articles,
    remove_duplicates
)

from database import (
    create_table,
    save_article,
    article_exists
)

from extractor import extract_article
from summariser import summarize
from scorer import score_article

from colorama import init, Fore, Style


init()


def print_colored_summary(summary):

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



def print_threat_score_breakdown(article):

    print("\nTHREAT SCORE BREAKDOWN")
    print("-" * 50)


    # Critical
    print("\nCritical Keywords (5 points each):")

    if article["critical_keywords"]:

        for keyword in article["critical_keywords"]:
            print(f"- {keyword}")

        critical_score = len(
            article["critical_keywords"]
        ) * 5

    else:

        print("None")
        critical_score = 0


    print(
        f"Contribution: {critical_score}"
    )



    # High
    print("\nHigh Keywords (3 points each):")

    if article["high_keywords"]:

        for keyword in article["high_keywords"]:
            print(f"- {keyword}")

        high_score = len(
            article["high_keywords"]
        ) * 3

    else:

        print("None")
        high_score = 0


    print(
        f"Contribution: {high_score}"
    )



    # Medium
    print("\nMedium Keywords (1 point each):")

    if article["medium_keywords"]:

        for keyword in article["medium_keywords"]:
            print(f"- {keyword}")

        medium_score = len(
            article["medium_keywords"]
        ) * 1

    else:

        print("None")
        medium_score = 0


    print(
        f"Contribution: {medium_score}"
    )


    print("\n")
    print("-" * 50)


    print(
        f"TOTAL SCORE: {article['score']}"
    )

    print(
        f"FINAL SEVERITY: {article['severity']}"
    )



def main():


    # INITIALIZE DATABASE

    create_table()



    # STEP 1: FETCH ARTICLES

    articles = fetch_articles()



  # Testing duplicate removal disabled
# articles = articles + articles


    total_fetched = len(articles)



    print("\nPIPELINE PROCESSING")

    print("-" * 50)


    print(
        f"Total fetched articles: {total_fetched}"
    )



    # STEP 2: FILTER RECENT ARTICLES

    recent_articles = filter_recent_articles(
        articles
    )


    print(
        f"Articles after 24-hour filtering: {len(recent_articles)}"
    )



    # STEP 3: REMOVE DUPLICATES

    unique_articles = remove_duplicates(
        recent_articles
    )


    print(
        f"Articles after duplicate removal: {len(unique_articles)}"
    )



    duplicates_removed = (
        len(recent_articles)
        -
        len(unique_articles)
    )


    new_articles = len(unique_articles)



    print("\nSUMMARY")

    print("-" * 50)


    print(
        f"{total_fetched} articles fetched, "
        f"{duplicates_removed} duplicates removed, "
        f"{new_articles} new articles"
    )



    print("\nFINAL ARTICLES")

    print("-" * 50)



    selected_articles = []

    source_count = {}

    for article in unique_articles:

        source = article["source"]

        if source_count.get(source, 0) < 2:
            selected_articles.append(article)
            source_count[source] = source_count.get(source, 0) + 1

        if len(selected_articles) == 10:
            break


    total_articles = len(selected_articles)



    for index, article in enumerate(
        selected_articles,
        start=1
    ):


        print(
            f"\n[{index}/{total_articles}] Processing article..."
        )



        if article_exists(article["url"]):

            print(
                f"Skipping duplicate: {article['title']}"
            )

            continue



        print("\n========================================")


        print("Title:")

        print(
            article["title"]
        )


        try:


            # STEP 4: EXTRACT ARTICLE

            print(
                "\nExtracting article..."
            )


            article_text = extract_article(
                article["url"]
            )



            if article_text:


                article["content"] = article_text


                print(
                    "Article extracted successfully."
                )



                # STEP 5: SUMMARY

                print(
                    "Generating summary with Groq AI..."
                )


                article["summary"] = summarize(
                    article["title"],
                    article_text
                )


            else:


                article["content"] = ""


                article["summary"] = (
                    "Unable to extract article."
                )


                print(
                    "Failed to extract article."
                )
                            # STEP 6: SCORE ARTICLE

            result = score_article(
                    article["title"],
                    article["summary"]
                )


            article["severity"] = result["severity"]

            article["score"] = result["score"]


            article["critical_keywords"] = (
                result["critical_keywords"]
            )


            article["high_keywords"] = (
                result["high_keywords"]
            )


            article["medium_keywords"] = (
                result["medium_keywords"]
            )



            # STEP 7: SAVE TO DATABASE

            save_article(article)



            # OUTPUT

            print("\nSAVED ARTICLE")

            print("-" * 50)



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



            print("\nSUMMARY")

            print("-" * 50)



            print_colored_summary(
                article["summary"]
            )



            # SCORE DETAILS

            print_threat_score_breakdown(
                article
            )



        except Exception as e:


            print(
                "\nERROR PROCESSING ARTICLE"
            )


            print(
                article["title"]
            )


            print(
                e
            )


            continue



    print(
        "\nPipeline completed successfully."
    )



if __name__ == "__main__":

    main()