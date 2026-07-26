from database import (
    get_critical_articles,
    mark_alert_sent
)


from alert import (
    should_alert,
    send_alert_email,
    send_no_news_email
)


from config import EMAIL_ADDRESS




articles = get_critical_articles()




if not articles:


    print(
        "No new critical alerts."
    )


    send_no_news_email(
        EMAIL_ADDRESS
    )



else:


    print(
        f"{len(articles)} new critical alerts found."
    )



    for article in articles:



        if should_alert(article):


            send_alert_email(

                article,

                EMAIL_ADDRESS

            )


            mark_alert_sent(

                article["id"]

            )