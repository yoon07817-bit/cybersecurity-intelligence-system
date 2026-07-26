import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_ADDRESS, EMAIL_PASSWORD



def send_email(to_email, articles):

    msg = MIMEMultipart("alternative")

    msg["Subject"] = "Daily Cybersecurity Digest"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email


    # Create HTML content
    html = """
    <html>
    <body>

    <h1>Daily Cybersecurity Digest</h1>

    <p>
    Latest cybersecurity news and threat intelligence.
    </p>

    """

    for article in articles:

        html += f"""

        <hr>

        <h2>{article['title']}</h2>

        <p>
        <b>Severity:</b> {article['severity']}/10
        </p>

        <p>
        {article['summary']}
        </p>

        <p>
        Source:
        <a href="{article['link']}">
        Read More
        </a>
        </p>

        """



    html += """

    </body>
    </html>
    """


    # Attach HTML email
    html_part = MIMEText(
        html,
        "html"
    )

    msg.attach(html_part)



    # Send email
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


        print("HTML email sent successfully!")


    except Exception as e:

        print("Email failed:")
        print(e)