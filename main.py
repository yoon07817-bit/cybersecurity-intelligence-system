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



def main():

    # INITIALIZE DATABASE
    create_table()


    # STEP 1: FETCH ARTICLES
    articles = fetch_articles()


    # Testing duplicate removal
    articles = articles + articles


    total_fetched = len(articles)


    print("\nPIPELINE PROCESSING")
    print("-" * 50)

    print(
        f"Total fetched articles: {total_fetched}"
    )


    # STEP 2: FILTER RECENT ARTICLES
    recent_articles = filter_recent_articles(articles)


    print(
        f"Articles after 24-hour filtering: {len(recent_articles)}"
    )


    # STEP 3: REMOVE DUPLICATES
    unique_articles = remove_duplicates(recent_articles)


    print(
        f"Articles after duplicate removal: {len(unique_articles)}"
    )


    duplicates_removed = (
        len(recent_articles) - len(unique_articles)
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



# PROCESS FIRST 10 ARTICLES
    selected_articles = unique_articles[:10]

    total_articles = len(selected_articles)


    for index, article in enumerate(
        selected_articles,
        start=1
    ):


        print(
            f"\n[{index}/{total_articles}] Processing article..."
        )


        # Skip articles already stored
        if article_exists(article["url"]):

            print(
                f"Skipping duplicate: {article['title']}"
            )

            continue



        print("\n========================================")

        print(
            "Title:"
        )

        print(
            article["title"]
        )


        try:


            # STEP 4: EXTRACT ARTICLE TEXT
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



                # STEP 5: GENERATE SUMMARY
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



            # DEFAULT SEVERITY
            article["severity"] = "Unknown"



            # STEP 6: SAVE TO DATABASE
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