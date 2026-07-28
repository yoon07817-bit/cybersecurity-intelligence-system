from emailer import send_email



# ==========================
# TEST ARTICLES
# ==========================

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



# ==========================
# TEST EMAIL RECEIVERS
# ==========================

test_emails = [

    "nandaroo9070@gmail.com",

    "yoon07817@gmail.com"

]



# ==========================
# SEND TEST EMAILS
# ==========================

for email in test_emails:

    print("\n")
    print("=" * 50)

    print(
        "Sending test email to:",
        email
    )

    print("=" * 50)


    try:

        send_email(
            email,
            test_articles
        )


        print(
            "Test completed for:",
            email
        )


    except Exception as e:

        print(
            "Failed sending to:",
            email
        )

        print(e)



print("\n")
print("All email tests completed.")