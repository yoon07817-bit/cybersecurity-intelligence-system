import json
import os

from dotenv import load_dotenv


# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()


# ==========================================================
# LOAD RSS FEEDS
# ==========================================================

with open(
    "rss_feeds.json",
    "r",
    encoding="utf-8"
) as file:

    RSS_FEEDS = json.load(file)


# ==========================================================
# GMAIL CREDENTIALS
# ==========================================================

EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)


if (
    EMAIL_ADDRESS is None
    or
    EMAIL_PASSWORD is None
):

    raise Exception(
        "Email credentials not found. "
        "Check your .env file."
    )


# ==========================================================
# SCHEDULER CONFIGURATION
# ==========================================================

# ----------------------------------------------------------
# TEST MODE
# ----------------------------------------------------------
#
# True  = temporary fast schedule for supervisor testing
# False = final production schedule
#
# ----------------------------------------------------------

TEST_MODE = True


# ==========================================================
# TESTING SCHEDULE
# ==========================================================

if TEST_MODE:

    # Collect security articles every 1 minute
    DATA_COLLECTION_INTERVAL = 60


    # Check Critical alerts every 2 minutes
    CRITICAL_ALERT_INTERVAL = 120


    # Daily digest will be tested manually
    DAILY_DIGEST_HOUR = None


# ==========================================================
# FINAL / PRODUCTION SCHEDULE
# ==========================================================

else:

    # Collect security articles every 10 minutes
    DATA_COLLECTION_INTERVAL = 600


    # Check Critical alerts every 1 hour
    CRITICAL_ALERT_INTERVAL = 3600


    # Daily digest at 7:00 AM
    DAILY_DIGEST_HOUR = 7