import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


from config import EMAIL_ADDRESS, EMAIL_PASSWORD


from database import get_users_for_alert


from severity_filter import allow_alert





def send_email(
        articles,
        alert_type="daily",
        subject=None,
        dashboard_url="http://192.168.1.13:5000"
):


    """
    Sends personalised security emails.

    alert_type:
    - daily
    - weekly
    - critical

    """



    # ======================================
    # GET SUBSCRIBED USERS
    # ======================================


    users = get_users_for_alert(
        alert_type
    )



    if not users:

        print(
            f"[{alert_type}] No subscribers found."
        )

        return




    # ======================================
    # FILTER ARTICLES
    # ======================================


    filtered_articles = []



    for article in articles:


        severity = article.get(
            "severity",
            "Low"
        )



        filtered_articles.append(
            article
        )



    if not filtered_articles:


        print(
            "No matching articles."
        )

        return





    # ======================================
    # SUBJECT
    # ======================================


    if not subject:


        if alert_type == "critical":

            subject = (
                "🚨 Critical Security Alert"
            )


        elif alert_type == "weekly":

            subject = (
                "📅 Weekly Security Digest"
            )


        else:

            subject = (
                "📰 Daily Security Digest"
            )






    # ======================================
    # SEND EMAIL TO EACH USER
    # ======================================


    try:


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


                email = user["email"]

                threshold = user["minimum_severity"]





                user_articles = []



                for article in filtered_articles:


                    if allow_alert(

                        article.get(
                            "severity",
                            "Low"
                        ),

                        threshold

                    ):

                        user_articles.append(
                            article
                        )




                if not user_articles:


                    continue





                html = """

                <html>

                <body>

                <h2>
                🛡️ Security Digest
                </h2>

                """





                for article in user_articles:


                    html += f"""

                    <hr>

                    <h3>
                    {article.get('title')}
                    </h3>


                    <p>
                    <b>Severity:</b>
                    {article.get('severity')}
                    </p>


                    <p>
                    {article.get('summary')}
                    </p>


                    <a href="{article.get('link',
                    article.get('url','#'))}">
                    Read More
                    </a>

                    """



                html += """

                </body>

                </html>

                """





                msg = MIMEMultipart(
                    "alternative"
                )


                msg["Subject"] = subject


                msg["From"] = EMAIL_ADDRESS


                msg["To"] = email



                msg.attach(
                    MIMEText(
                        html,
                        "html"
                    )
                )



                smtp.send_message(
                    msg
                )



                print(
                    f"Email sent -> {email}"
                )





    except Exception as e:


        print(
            "Email failed:",
            e
        )






if __name__ == "__main__":


    print(
        "Emailer test completed."
    )