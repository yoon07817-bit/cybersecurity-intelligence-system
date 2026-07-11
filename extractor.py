import trafilatura


def extract_article(url):
    """
    Download and extract the main article text.
    """

    try:
        downloaded = trafilatura.fetch_url(url)

        if downloaded is None:
            return None

        text = trafilatura.extract(downloaded)

        return text

    except Exception as e:
        print(f"Extraction failed: {e}")
        return None