from emailer import send_email



test_articles = [

    {
        "title": "Critical Linux Vulnerability Discovered",

        "severity": 9,

        "summary":
        "A critical vulnerability allows attackers to execute malicious commands remotely.",

        "link":
        "https://example.com"
    },


    {
        "title": "New Phishing Campaign Targets Users",

        "severity": 7,

        "summary":
        "Attackers are sending fake login pages to steal credentials.",

        "link":
        "https://example.com"
    }

]



send_email(
    "nandaroo9070@gmail.com",
    test_articles
)