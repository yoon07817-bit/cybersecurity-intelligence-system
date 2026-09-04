import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD
)


from database import (
    get_critical_articles,
    get_users_for_alert,
    mark_alert_sent
)


from severity_filter import allow_alert





# ==========================================
# CHECK WHETHER ARTICLE NEEDS ALERT
# ==========================================

def should_alert(article):

    critical_keywords = [

        "zero-day",

        "actively exploited",

        "poc released"

    ]


    text = (

        article.get("title", "")

        +

        article.get("summary", "")

    ).lower()



    for keyword in critical_keywords:

        if keyword in text:

            return True



    if article.get("severity") == "Critical":

        return True



    return False






# ==========================================
# SEND EMAIL ALERT
# ==========================================

def send_alert_email(article):


    users = get_users_for_alert(
        "critical"
    )


    if not users:

        print(
            "No critical subscribers."
        )

        return False



    successful_send = False



    try:


        # Open SMTP connection once

        with smtplib.SMTP(
            "smtp.gmail.com",
            587
        ) as smtp:


            smtp.starttls()


            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )



            for user in users:



                # Check user's severity preference

                if not allow_alert(

                    article.get(
                        "severity",
                        "Low"
                    ),

                    user["minimum_severity"]

                ):

                    continue





                html = f"""

                <html>

                <body style="font-family: Arial;">


                <h2>
                🚨 Critical Security Alert
                </h2>


                <h3>
                {article.get('title', 'Security Threat')}
                </h3>


                <p>
                <b>Severity:</b>
                {article.get('severity', 'Unknown')}
                </p>


                <p>
                <b>Threat Score:</b>
                {article.get('score', 'N/A')}
                </p>


                <p>
                {article.get('summary', 'No summary available')}
                </p>


                </body>

                </html>

                """





                msg = MIMEMultipart(
                    "alternative"
                )


                msg["Subject"] = (

                    "🚨 Critical Security Alert"

                )


                msg["From"] = EMAIL_ADDRESS


                msg["To"] = user["email"]



                msg.attach(

                    MIMEText(
                        html,
                        "html"
                    )

                )



                smtp.send_message(msg)



                print(

                    "Critical alert sent:",

                    user["email"]

                )



                successful_send = True




    except Exception as e:


        print(

            "Alert failed:",

            e

        )


        return False





    return successful_send







# ==========================================
# PROCESS UNSENT CRITICAL ALERTS
# ==========================================

def process_unhandled_critical_alerts():



    articles = get_critical_articles()



    if not articles:


        print(
            "No un-sent critical alerts."
        )


        return





    for article in articles:



        # Convert sqlite Row to dictionary

        article = dict(article)



        print(

            "Checking:",

            article.get("title")

        )



        if should_alert(article):



            sent = send_alert_email(
                article
            )



            if sent:



                mark_alert_sent(

                    article["id"]

                )


                print(

                    "Alert completed:",

                    article["title"]

                )



        else:


            print(

                "Alert condition not matched:",

                article["title"]

            )








# ==========================================
# MANUAL TEST
# ==========================================

if __name__ == "__main__":


    print(
        "Running Critical Alert Check..."
    )


    process_unhandled_critical_alerts()