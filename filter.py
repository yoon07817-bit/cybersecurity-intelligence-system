def filter_news(articles):
    """
    Filters news articles:
    - removes duplicate titles
    """

    seen = set()
    filtered = []

    for article in articles:
        title = article["title"]

        # skip duplicates
        if title in seen:
            continue

        seen.add(title)
        filtered.append(article)

    return filtered