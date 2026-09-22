from database import (
    create_table,
    get_critical_articles,
    mark_alert_sent
)

from alert import (
    should_alert,
    send_alert_email
)


# ==========================================================
# HOURLY CRITICAL SECURITY ALERT CHECK
# ==========================================================

def run_alert_check():

    print("\n")

    print("=" * 60)

    print(
        "HOURLY SECURITY ALERT CHECK"
    )

    print("=" * 60)


    # ======================================================
    # STEP 1 — ENSURE DATABASE EXISTS
    # ======================================================

    try:

        create_table()

    except Exception as e:

        print(
            "Database initialization failed:",
            e
        )

        return


    # ======================================================
    # STEP 2 — GET UNSENT CRITICAL ARTICLES
    # ======================================================
    #
    # IMPORTANT:
    #
    # This function DOES NOT fetch RSS feeds.
    #
    # The articles have already been collected,
    # processed and stored by main.py.
    #
    # get_critical_articles() retrieves the Critical
    # articles that are waiting for an alert.
    #
    # ======================================================

    try:

        critical_articles = (
            get_critical_articles()
        )

    except Exception as e:

        print(
            "Failed to retrieve critical articles:",
            e
        )

        return


    # ======================================================
    # STEP 3 — NO UNSENT CRITICAL ARTICLES
    # ======================================================

    if not critical_articles:

        print(
            "\nNo un-sent Critical alerts."
        )

        return


    print(

        f"\n{len(critical_articles)} "
        f"Critical alert(s) ready."

    )


    # ======================================================
    # STEP 4 — PROCESS EACH CRITICAL ARTICLE
    # ======================================================

    for row in critical_articles:

        try:

            # ------------------------------------------------
            # Convert SQLite Row to dictionary
            # ------------------------------------------------

            article = dict(
                row
            )


            print(
                "\nPreparing alert:",
                article.get(
                    "title",
                    "Unknown"
                )
            )


            # ==================================================
            # CHECK ALERT CONDITION
            # ==================================================

            if not should_alert(
                article
            ):

                print(
                    "Alert condition not matched:",
                    article.get(
                        "title",
                        "Unknown"
                    )
                )

                continue


            print(
                "Alert condition matched."
            )


            # ==================================================
            # SEND EMAIL
            # ==================================================

            try:

                sent = send_alert_email(
                    article
                )

            except Exception as e:

                print(
                    "Email sending failed:",
                    e
                )

                sent = False


            # ==================================================
            # MARK AS SENT ONLY AFTER SUCCESS
            # ==================================================

            if sent:

                try:

                    mark_alert_sent(
                        article["id"]
                    )


                    print(
                        "Alert sent:",
                        article.get(
                            "title",
                            "Unknown"
                        )
                    )


                except Exception as e:

                    print(
                        "Failed to mark alert as sent:",
                        e
                    )


            else:

                print(
                    "Alert was NOT sent:",
                    article.get(
                        "title",
                        "Unknown"
                    )
                )


        except Exception as e:

            print(
                "Alert processing failed:",
                e
            )


    # ======================================================
    # COMPLETE
    # ======================================================

    print(
        "\nCritical alert check completed."
    )


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == "__main__":

    run_alert_check()