import smtplib
from email.message import EmailMessage

from config import EMAIL_ADDRESS, EMAIL_PASSWORD


msg = EmailMessage()

msg["Subject"] = "Security Digest Test Email"
msg["From"] = EMAIL_ADDRESS
msg["To"] = EMAIL_ADDRESS


msg.set_content(
"""
Hello,

This is a test email sent from my Cybersecurity Digest project.

SMTP integration is working successfully.

Regards,
Security Digest System
"""
)


try:

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:

        smtp.starttls()

        smtp.login(
            EMAIL_ADDRESS,
            EMAIL_PASSWORD
        )

        smtp.send_message(msg)


    print("Email sent successfully!")


except Exception as error:

    print("Email sending failed:")
    print(error)