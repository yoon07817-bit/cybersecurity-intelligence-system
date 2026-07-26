import json
import os
from dotenv import load_dotenv


# Load RSS feeds
with open("rss_feeds.json", "r", encoding="utf-8") as file:
    RSS_FEEDS = json.load(file)


# Load .env
load_dotenv()


# Gmail credentials
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


if EMAIL_ADDRESS is None or EMAIL_PASSWORD is None:
    raise Exception(
        "Email credentials not found. Check your .env file."
    )