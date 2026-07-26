from fetcher import fetch_articles
from summariser import summarize
from scorer import score_article

from database import (
    create_table,
    save_article,
    get_critical_articles,
    mark_alert_sent
)

from alert import (
    should_alert,
    send_alert_email
)

from config import EMAIL_ADDRESS



def run_alert_check():

    print("\n")
    print("=" * 50)
    print("HOURLY SECURITY ALERT CHECK")
    print("=" * 50)



    # Create database

    create_table()



    # ==========================
    # FETCH RSS ARTICLES
    # ==========================

    articles = fetch_articles()


    print(
        f"Fetched {len(articles)} articles"
    )



    # ==========================
    # CHECK ONLY CRITICAL
    # ==========================

    for article in articles:


        try:


            print(
                "\nChecking:",
                article["title"]
            )



            # Quick scoring first

            quick_result = score_article(

                article["title"],

                article.get(
                    "description",
                    ""
                )

            )



            # Ignore non-critical

            if quick_result["severity"] != "Critical":

                print(
                    "Not Critical - skipped"
                )

                continue



            print(
                "CRITICAL ARTICLE FOUND!"
            )



            # Get article body

            text = article.get(
                "content",
                ""
            )


            if not text:

                text = article.get(
                    "description",
                    article["title"]
                )



            # AI summary only for Critical

            summary = summarize(

                article["title"],

                text

            )



            # Final score

            result = score_article(

                article["title"],

                summary

            )



            article["summary"] = summary

            article["score"] = result["score"]

            article["severity"] = result["severity"]



            # Save Critical article

            save_article(article)



        except Exception as e:


            print(
                "Processing failed:",
                e
            )





    # ==========================
    # SEND ALERT EMAIL
    # ==========================

    critical_articles = get_critical_articles()



    if not critical_articles:


        print(
            "No new Critical alerts."
        )

        return




    print(

        f"{len(critical_articles)} Critical alerts found."

    )



    for article in critical_articles:


        if should_alert(article):


            send_alert_email(

                article,

                EMAIL_ADDRESS

            )


            mark_alert_sent(

                article["id"]

            )


            print(

                "Alert sent:",

                article["title"]

            )





if __name__ == "__main__":

    run_alert_check()