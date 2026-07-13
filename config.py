import json

with open("rss_feeds.json", "r", encoding="utf-8") as file:
    RSS_FEEDS = json.load(file)