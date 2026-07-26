import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_ADDRESS, EMAIL_PASSWORD



# CHECK IF ARTICLE SHOULD ALERT
def should_alert(article):

    critical_keywords = [

        "zero-day",
        "actively exploited",
        "poc released"

    ]


    text = (

        article["title"]

        + " "

        + article["summary"]

    ).lower()



    for keyword in critical_keywords:

        if keyword in text:

            return True



    if article["severity"] == "Critical":

        return True



    return False





# SEND CRITICAL ALERT EMAIL
def send_alert_email(article, recipient):


    msg = MIMEMultipart("alternative")


    msg["Subject"] = (
        "🚨 Critical Security Alert"
    )


    msg["From"] = EMAIL_ADDRESS

    msg["To"] = recipient



    html = f"""

    <html>

    <body>


    <h2>
    🚨 Critical Security Alert
    </h2>


    <h3>
    {article["title"]}
    </h3>



    <p>

    <b>
    Severity:
    </b>

    🔴 {article["severity"]}

    </p>



    <p>

    <b>
    Score:
    </b>

    {article["score"]}

    </p>



    <p>

    {article["summary"]}

    </p>



    <p>

    <a href="{article["link"]}">
    Read Full Article
    </a>

    </p>



    </body>

    </html>

    """



    msg.attach(
        MIMEText(
            html,
            "html"
        )
    )



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


            smtp.send_message(msg)



        print(
            "🚨 Alert sent!"
        )



    except Exception as e:


        print(
            "Alert email failed:"
        )


        print(e)





# SEND NO NEWS EMAIL
def send_no_news_email(recipient):


    msg = MIMEMultipart("alternative")


    msg["Subject"] = (
        "Daily Security Alert"
    )


    msg["From"] = EMAIL_ADDRESS


    msg["To"] = recipient




    html = """

    <html>

    <body>


    <h2>
    Daily Security Alert
    </h2>



    <p>
    No new alerts today.
    </p>



    <p>

    No Critical cybersecurity threats
    were detected.

    </p>



    </body>

    </html>

    """



    msg.attach(
        MIMEText(
            html,
            "html"
        )
    )



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


            smtp.send_message(msg)



        print(
            "No-news email sent!"
        )



    except Exception as e:


        print(
            "No-news email failed:"
        )


        print(e)