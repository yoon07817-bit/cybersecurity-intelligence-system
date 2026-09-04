from fetcher import fetch_articles
from summariser import summarize
from scorer import score_article


from database import (
    create_table,
    save_article,
    article_exists,
    get_critical_articles,
    mark_alert_sent
)


from alert import (
    should_alert,
    send_alert_email
)




# ==========================================
# HOURLY SECURITY ALERT CHECK
# ==========================================


def run_alert_check():


    print("\n")
    print("=" * 60)
    print("HOURLY SECURITY ALERT CHECK")
    print("=" * 60)




    # Create database tables if missing

    create_table()




    # ======================================
    # FETCH SECURITY NEWS
    # ======================================

    try:

        articles = fetch_articles()


        print(
            f"Fetched {len(articles)} articles"
        )


    except Exception as e:


        print(
            "RSS fetching failed:",
            e
        )


        return





    # ======================================
    # PROCESS ARTICLES
    # ======================================


    for article in articles:


        try:


            title = article.get(
                "title",
                "Unknown"
            )


            print(
                "\nChecking:",
                title
            )



            description = article.get(
                "description",
                ""
            )



            # ------------------------------
            # Quick Threat Scoring
            # ------------------------------


            quick_result = score_article(

                title,

                description

            )



            if quick_result["severity"] != "Critical":


                print(
                    "Not Critical - skipped"
                )


                continue




            print(
                "CRITICAL ARTICLE FOUND!"
            )





            # ------------------------------
            # Check duplicate article
            # ------------------------------


            if article_exists(
                article["url"]
            ):


                print(
                    "Already exists - skipped"
                )


                continue






            # ------------------------------
            # Generate Summary
            # ------------------------------


            content = article.get(
                "content",
                ""
            )



            if not content:


                content = description or title





            summary = summarize(

                title,

                content

            )






            # ------------------------------
            # Final scoring
            # ------------------------------


            final_result = score_article(

                title,

                summary

            )




            article["summary"] = summary

            article["score"] = (
                final_result["score"]
            )

            article["severity"] = (
                final_result["severity"]
            )





            # Save only critical article


            save_article(
                article
            )



            print(
                "Critical article saved:",
                title
            )



        except Exception as e:


            print(
                "Article processing failed:",
                e
            )







    # ======================================
    # SEND CRITICAL ALERTS
    # ======================================


    critical_articles = get_critical_articles()



    if not critical_articles:


        print(
            "\nNo new Critical alerts."
        )


        return





    print(

        f"\n{len(critical_articles)} Critical alert(s) ready."

    )





    for article in critical_articles:


        try:


            if should_alert(article):


                send_alert_email(
                    article
                )



                mark_alert_sent(
                    article["id"]
                )



                print(
                    "Alert sent:",
                    article["title"]
                )



            else:


                print(
                    "Alert condition not matched:",
                    article["title"]
                )





        except Exception as e:


            print(
                "Alert sending failed:",
                e
            )







# ==========================================
# MANUAL TEST
# ==========================================


if __name__ == "__main__":


    run_alert_check()