import smtplib
import html
import re
import os

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


# ==========================================================
# CONFIGURATION
# ==========================================================

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Dashboard URL:
# - Render: set DASHBOARD_URL environment variable
# - Local: defaults to localhost
DEFAULT_DASHBOARD_URL = os.getenv(
    "DASHBOARD_URL",
    "http://127.0.0.1:5000/"
).rstrip("/") + "/"


# ==========================================================
# CHECK WHETHER ARTICLE NEEDS ALERT
# ==========================================================

def should_alert(article):

    critical_keywords = [
        "zero-day",
        "actively exploited",
        "poc released"
    ]

    title = str(
        article.get(
            "title",
            ""
        )
    )

    summary = str(
        article.get(
            "summary",
            ""
        )
    )

    text = (
        title
        + " "
        + summary
    ).lower()

    # ------------------------------------------------------
    # Check critical keywords
    # ------------------------------------------------------

    for keyword in critical_keywords:

        if keyword in text:

            return True

    # ------------------------------------------------------
    # Check severity
    # ------------------------------------------------------

    severity = str(
        article.get(
            "severity",
            "Low"
        )
    ).lower()

    if severity == "critical":

        return True

    return False


# ==========================================================
# CLEAN MARKDOWN SUMMARY
# ==========================================================

def clean_summary(summary):

    if not summary:

        return "<p>No summary available.</p>"

    summary = str(
        summary
    )

    # Escape HTML

    summary = html.escape(
        summary
    )

    # ------------------------------------------------------
    # Markdown headings
    # ------------------------------------------------------

    summary = re.sub(
        r"##\s*\*\*(.*?)\*\*",
        r"<h4>\1</h4>",
        summary
    )

    # ------------------------------------------------------
    # Bold text
    # ------------------------------------------------------

    summary = re.sub(
        r"\*\*(.*?)\*\*",
        r"<strong>\1</strong>",
        summary
    )

    # ------------------------------------------------------
    # Convert lines
    # ------------------------------------------------------

    lines = summary.split(
        "\n"
    )

    output = []

    in_list = False

    for line in lines:

        line = line.strip()

        # Bullet point

        if line.startswith("- "):

            if not in_list:

                output.append(
                    "<ul>"
                )

                in_list = True

            output.append(
                f"<li>{line[2:]}</li>"
            )

        else:

            if in_list:

                output.append(
                    "</ul>"
                )

                in_list = False

            if line:

                if (
                    line.startswith("<h4>")
                    and line.endswith("</h4>")
                ):

                    output.append(
                        line
                    )

                else:

                    output.append(
                        f"<p>{line}</p>"
                    )

    if in_list:

        output.append(
            "</ul>"
        )

    return "\n".join(
        output
    )


# ==========================================================
# GET CVE INFORMATION
# ==========================================================

def get_article_cves(article):

    """
    Get CVE identifiers stored in the article.

    Supports:
        cves
        cve_ids
        cve
    """

    cves = []

    if article.get("cves"):

        cves = article["cves"]

    elif article.get("cve_ids"):

        cves = article["cve_ids"]

    elif article.get("cve"):

        cves = article["cve"]

    if isinstance(
        cves,
        str
    ):

        cves = [
            cves
        ]

    if not isinstance(
        cves,
        list
    ):

        cves = [
            cves
        ]

    return cves


# ==========================================================
# FORMAT CVE INFORMATION
# ==========================================================

def format_cves(article):

    cves = get_article_cves(
        article
    )

    # ------------------------------------------------------
    # No CVE
    # ------------------------------------------------------

    if not cves:

        return """

        <div
            style="
                background:#f8f9fa;
                border:1px solid #dee2e6;
                padding:12px;
                border-radius:5px;
            "
        >

            <em>No CVE detected.</em>

        </div>

        """

    # ------------------------------------------------------
    # CVE list
    # ------------------------------------------------------

    cve_html = """

    <div
        style="
            background:#f8f9fa;
            border:1px solid #dee2e6;
            padding:12px;
            border-radius:5px;
        "
    >

    <ul
        style="
            margin:0;
            padding-left:20px;
        "
    >

    """

    for cve in cves:

        if isinstance(
            cve,
            dict
        ):

            cve_id = cve.get(
                "cve_id",
                cve.get(
                    "id",
                    "Unknown CVE"
                )
            )

        else:

            cve_id = cve

        cve_html += (

            "<li "
            "style='margin-bottom:6px;'>"

            "<strong>"

            + html.escape(
                str(cve_id)
            )

            + "</strong>"

            "</li>"

        )

    cve_html += """

    </ul>

    </div>

    """

    return cve_html


# ==========================================================
# GET PROTECTION RECOMMENDATION
# ==========================================================

def get_article_recommendation(article):

    recommendation = article.get(
        "recommendation"
    )

    if not recommendation:

        category = article.get(
            "category",
            "General Security"
        )

        severity = article.get(
            "severity",
            "Low"
        )

        # Try to import recommendation function
        # only if the article does not already contain
        # a recommendation.

        try:

            from database import (
                get_recommendation
            )

            recommendation = (
                get_recommendation(
                    category,
                    severity
                )
            )

        except Exception:

            recommendation = None

    # ------------------------------------------------------
    # Final fallback
    # ------------------------------------------------------

    if not recommendation:

        recommendation = (

            "Review the affected systems, "
            "apply available security updates, "
            "monitor for suspicious activity, "
            "review access controls, and follow "
            "appropriate cybersecurity best practices."

        )

    return recommendation


# ==========================================================
# SEVERITY STYLE
# ==========================================================

def get_severity_style(
    severity
):

    severity = str(
        severity
    ).lower()

    if severity == "critical":

        return (
            "color:#dc3545;"
            "font-weight:bold;"
        )

    elif severity == "high":

        return (
            "color:#fd7e14;"
            "font-weight:bold;"
        )

    elif severity == "medium":

        return (
            "color:#b8860b;"
            "font-weight:bold;"
        )

    else:

        return (
            "color:#198754;"
            "font-weight:bold;"
        )


# ==========================================================
# SEND CRITICAL ALERT EMAIL
# ==========================================================

def send_alert_email(
    article,
    dashboard_url=DEFAULT_DASHBOARD_URL
):

    # ======================================================
    # GET CRITICAL SUBSCRIBERS
    # ======================================================

    try:

        users = get_users_for_alert(
            "critical"
        )

    except Exception as e:

        print(
            "Failed to get critical subscribers:",
            e
        )

        return False

    if not users:

        print(
            "No critical subscribers."
        )

        return False

    successful_send = False

    # ======================================================
    # PREPARE ARTICLE DATA
    # ======================================================

    title = str(
        article.get(
            "title",
            "Security Threat"
        )
    )

    severity = str(
        article.get(
            "severity",
            "Critical"
        )
    )

    category = str(
        article.get(
            "category",
            "General Security"
        )
    )

    source = str(
        article.get(
            "source",
            "Unknown"
        )
    )

    score = article.get(
        "score",
        "N/A"
    )

    published_date = str(
        article.get(
            "published_date",
            "N/A"
        )
    )

    article_url = article.get(
        "link",
        article.get(
            "url",
            "#"
        )
    )

    recommendation = (
        get_article_recommendation(
            article
        )
    )

    summary = clean_summary(
        article.get(
            "summary",
            ""
        )
    )

    cve_html = format_cves(
        article
    )

    # ======================================================
    # ESCAPE TEXT
    # ======================================================

    title_safe = html.escape(
        title
    )

    severity_safe = html.escape(
        severity
    )

    category_safe = html.escape(
        category
    )

    source_safe = html.escape(
        source
    )

    score_safe = html.escape(
        str(score)
    )

    date_safe = html.escape(
        published_date
    )

    recommendation_safe = html.escape(
        str(recommendation)
    )

    article_url_safe = html.escape(
        str(article_url),
        quote=True
    )

    dashboard_url_safe = html.escape(
        str(dashboard_url),
        quote=True
    )

    severity_style = (
        get_severity_style(
            severity
        )
    )

    # ======================================================
    # SMTP CONNECTION
    # ======================================================

    try:

        with smtplib.SMTP(
            SMTP_SERVER,
            SMTP_PORT
        ) as smtp:

            smtp.starttls()

            smtp.login(
                EMAIL_ADDRESS,
                EMAIL_PASSWORD
            )

            print(
                "Connected to Gmail SMTP."
            )

            # ==================================================
            # SEND TO EACH USER
            # ==================================================

            for user in users:

                # Convert database row to dictionary

                user = dict(
                    user
                )

                email = user.get(
                    "email"
                )

                if not email:

                    continue

                minimum_severity = (
                    user.get(
                        "minimum_severity",
                        "Low"
                    )
                )

                # ------------------------------------------------
                # Respect user's severity preference
                # ------------------------------------------------

                if not allow_alert(

                    severity,

                    minimum_severity

                ):

                    print(
                        f"Skipped {email}: "
                        f"severity preference"
                    )

                    continue

                # ==================================================
                # BUILD EMAIL
                # ==================================================

                html_body = f"""

                <!DOCTYPE html>

                <html>

                <head>

                    <meta charset="UTF-8">

                    <title>
                        Critical Security Alert
                    </title>

                </head>


                <body
                    style="
                        margin:0;
                        padding:20px;
                        background:#f5f7fa;
                        font-family:Arial,
                        Helvetica,sans-serif;
                        color:#212529;
                    "
                >


                <div
                    style="
                        max-width:700px;
                        margin:0 auto;
                        background:#ffffff;
                        padding:30px;
                        border-radius:10px;
                        box-shadow:
                        0 2px 8px
                        rgba(0,0,0,0.08);
                    "
                >


                <!-- HEADER -->

                <h2
                    style="
                        margin-top:0;
                        color:#dc3545;
                    "
                >

                    🚨 Critical Security Alert

                </h2>


                <p
                    style="
                        color:#6c757d;
                    "
                >

                    Security Digest has detected
                    a potentially critical cybersecurity
                    event.

                </p>


                <!-- TITLE -->

                <div
                    style="
                        margin-top:25px;
                        padding:20px;
                        border:1px solid #dee2e6;
                        border-radius:8px;
                    "
                >


                <h3
                    style="
                        margin-top:0;
                    "
                >

                    {title_safe}

                </h3>


                <!-- SEVERITY -->

                <p>

                    <strong>
                        Severity:
                    </strong>

                    <span
                        style="{severity_style}"
                    >

                        {severity_safe}

                    </span>

                </p>


                <!-- CATEGORY -->

                <p>

                    <strong>
                        Category:
                    </strong>

                    {category_safe}

                </p>


                <!-- SCORE -->

                <p>

                    <strong>
                        Threat Score:
                    </strong>

                    {score_safe}

                </p>


                <!-- SOURCE -->

                <p>

                    <strong>
                        Source:
                    </strong>

                    {source_safe}

                </p>


                <!-- PUBLISHED DATE -->

                <p>

                    <strong>
                        Published:
                    </strong>

                    {date_safe}

                </p>


                <!-- SUMMARY -->

                <h4
                    style="
                        margin-top:25px;
                        border-bottom:
                        1px solid #dee2e6;
                        padding-bottom:7px;
                    "
                >

                    Summary

                </h4>


                <div>

                    {summary}

                </div>


                <!-- CVE INFORMATION -->

                <h4
                    style="
                        margin-top:25px;
                        border-bottom:
                        1px solid #dee2e6;
                        padding-bottom:7px;
                    "
                >

                    CVE Information

                </h4>


                <div>

                    {cve_html}

                </div>


                <!-- PROTECTION RECOMMENDATION -->

                <h4
                    style="
                        margin-top:25px;
                        border-bottom:
                        1px solid #dee2e6;
                        padding-bottom:7px;
                    "
                >

                    Protection Recommendation

                </h4>


                <div
                    style="
                        background:#f1f3f5;
                        border-left:
                        5px solid #0d6efd;
                        padding:15px;
                        border-radius:5px;
                        line-height:1.6;
                    "
                >

                    {recommendation_safe}

                </div>


                <!-- READ ORIGINAL ARTICLE -->

                <div
                    style="
                        margin-top:25px;
                    "
                >

                    <a
                        href="{article_url_safe}"
                        target="_blank"
                        style="
                            display:inline-block;
                            background:#0d6efd;
                            color:#ffffff;
                            padding:10px 16px;
                            text-decoration:none;
                            border-radius:5px;
                        "
                    >

                        Read Original Article ↗

                    </a>

                </div>


                </div>


                <!-- DASHBOARD -->

                <div
                    style="
                        margin-top:25px;
                        text-align:center;
                    "
                >

                    <a
                        href="{dashboard_url_safe}"
                        target="_blank"
                        style="
                            display:inline-block;
                            background:#212529;
                            color:#ffffff;
                            padding:11px 20px;
                            text-decoration:none;
                            border-radius:5px;
                        "
                    >

                        Open Security Dashboard

                    </a>

                </div>


                <!-- FOOTER -->

                <p
                    style="
                        margin-top:30px;
                        color:#6c757d;
                        font-size:12px;
                        text-align:center;
                    "
                >

                    This alert was generated automatically
                    by the Security Digest System.

                </p>


                </div>

                </body>

                </html>

                """


                # ==================================================
                # CREATE EMAIL
                # ==================================================

                msg = MIMEMultipart(
                    "alternative"
                )

                msg["Subject"] = (
                    "🚨 Critical Security Alert"
                )

                msg["From"] = (
                    EMAIL_ADDRESS
                )

                msg["To"] = (
                    email
                )

                msg.attach(
                    MIMEText(
                        html_body,
                        "html",
                        "utf-8"
                    )
                )


                # ==================================================
                # SEND
                # ==================================================

                smtp.send_message(
                    msg
                )

                print(
                    "Critical alert sent:",
                    email
                )

                successful_send = True


    # ==========================================================
    # GMAIL AUTHENTICATION ERROR
    # ==========================================================

    except smtplib.SMTPAuthenticationError:

        print(
            "Alert failed: Gmail authentication failed."
        )

        print(
            "Check EMAIL_ADDRESS and "
            "EMAIL_PASSWORD."
        )

        print(
            "Use a Gmail App Password if "
            "2-Step Verification is enabled."
        )

        return False


    # ==========================================================
    # SMTP ERROR
    # ==========================================================

    except smtplib.SMTPException as e:

        print(
            "Alert failed: SMTP error:",
            e
        )

        return False


    # ==========================================================
    # GENERAL ERROR
    # ==========================================================

    except Exception as e:

        print(
            "Alert failed:",
            e
        )

        return False


    return successful_send


# ==========================================================
# PROCESS UNSENT CRITICAL ALERTS
# ==========================================================

def process_unhandled_critical_alerts():

    try:

        articles = get_critical_articles()

    except Exception as e:

        print(
            "Failed to retrieve critical articles:",
            e
        )

        return

    if not articles:

        print(
            "No un-sent critical alerts."
        )

        return

    print(
        f"Found {len(articles)} "
        f"un-sent critical article(s)."
    )

    # ======================================================
    # PROCESS EACH ARTICLE
    # ======================================================

    for article in articles:

        # Convert database row to dictionary

        article = dict(
            article
        )

        print(
            "\nChecking:",
            article.get(
                "title",
                "Unknown Article"
            )
        )

        # --------------------------------------------------
        # Check alert condition
        # --------------------------------------------------

        if should_alert(
            article
        ):

            sent = send_alert_email(
                article
            )

            if sent:

                try:

                    mark_alert_sent(
                        article["id"]
                    )

                    print(
                        "Alert completed:",
                        article.get(
                            "title"
                        )
                    )

                except Exception as e:

                    print(
                        "Email sent but failed "
                        "to mark alert as sent:",
                        e
                    )

            else:

                print(
                    "Alert was not sent:"
                    " no eligible subscriber "
                    "or email failure."
                )

        else:

            print(
                "Alert condition not matched:",
                article.get(
                    "title"
                )
            )


# ==========================================================
# MANUAL TEST
# ==========================================================

if __name__ == "__main__":

    print(
        "Running Critical Alert Check..."
    )

    process_unhandled_critical_alerts()