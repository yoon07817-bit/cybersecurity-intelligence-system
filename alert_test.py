from scorer import score_article
from alert import should_alert, send_alert_email


title = "Microsoft confirms actively exploited zero-day vulnerability"


summary = """
Attackers are actively exploiting this zero-day vulnerability.
"""


result = score_article(
    title,
    summary
)


article = {

    "title": title,

    "summary": summary,

    "severity": result["severity"],

    "score": result["score"],

    "link": "https://example.com"

}


print(article)


if should_alert(article):

    send_alert_email(
        article,
        "nandaroo9070@gmail.com"
    )

else:

    print("No alert")