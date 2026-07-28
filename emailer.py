import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_ADDRESS, EMAIL_PASSWORD



def send_email(to_email, articles):


    msg = MIMEMultipart("alternative")


    msg["Subject"] = "Daily Cybersecurity Digest"

    msg["From"] = EMAIL_ADDRESS

    msg["To"] = to_email



    # ==========================
    # REMOVE DUPLICATES
    # ==========================

    unique_articles = []

    seen_urls = set()


    for article in articles:

        url = article.get(
            "link",
            article.get("url", "")
        )


        if url in seen_urls:
            continue


        seen_urls.add(url)

        unique_articles.append(article)



    # ==========================
    # CREATE HTML EMAIL
    # ==========================


    html = """
    <html>

    <body>


    <h1>
    Daily Cybersecurity Digest
    </h1>


    <p>
    Latest cybersecurity news and threat intelligence.
    </p>

    """



    for article in unique_articles:


        link = article.get(
            "link",
            article.get("url", "#")
        )


        html += f"""

        <hr>


        <h2>
        {article.get('title', 'No title')}
        </h2>


        <p>
        <b>Severity:</b>
        {article.get('severity', 'Unknown')}
        </p>


        <p>
        {article.get('summary', 'No summary available')}
        </p>


        <p>
        Source:
        <a href="{link}">
        Read More
        </a>
        </p>


        """



    # ==========================
    # UNSUBSCRIBE FOOTER
    # ==========================


    html += """

    <hr>


    <p style="font-size:12px;color:gray;">

    You are receiving this email because you subscribed
    to the Security Digest System.


    <br><br>


    If you no longer wish to receive these emails,
    please contact the administrator to unsubscribe.

    </p>


    </body>

    </html>

    """



    # Attach HTML email

    html_part = MIMEText(
        html,
        "html"
    )


    msg.attach(html_part)



    # ==========================
    # SEND EMAIL
    # ==========================


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
            "HTML email sent successfully!"
        )



    except Exception as e:


        print(
            "Email failed:"
        )

        print(e)