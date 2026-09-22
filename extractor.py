import requests
import trafilatura


# ==========================================================
# CONFIGURATION
# ==========================================================

REQUEST_TIMEOUT = 15


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


# ==========================================================
# ARTICLE EXTRACTION
# ==========================================================

def extract_article(url):
    """
    Download and extract the main article text.

    Requests is used for controlled timeout handling,
    while Trafilatura is used to extract the main
    article content.
    """

    if not url:
        return None


    try:

        print(
            "Downloading article..."
        )


        # --------------------------------------------------
        # Download webpage with timeout
        # --------------------------------------------------

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT
            },
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True
        )


        # --------------------------------------------------
        # HTTP status check
        # --------------------------------------------------

        response.raise_for_status()


        # --------------------------------------------------
        # Get HTML
        # --------------------------------------------------

        downloaded = response.text


        if not downloaded:

            print(
                "[WARNING] Website returned empty content."
            )

            return None


        # --------------------------------------------------
        # Extract main article
        # --------------------------------------------------

        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False
        )


        if not text:

            print(
                "[WARNING] No main article text "
                "could be extracted."
            )

            return None


        print(
            "Article extraction completed."
        )


        return text


    # ======================================================
    # TIMEOUT
    # ======================================================

    except requests.exceptions.Timeout:

        print(
            "[WARNING] Article download timed out "
            f"after {REQUEST_TIMEOUT} seconds."
        )

        return None


    # ======================================================
    # CONNECTION ERROR
    # ======================================================

    except requests.exceptions.ConnectionError:

        print(
            "[WARNING] Could not connect to article website."
        )

        return None


    # ======================================================
    # HTTP ERROR
    # ======================================================

    except requests.exceptions.HTTPError as e:

        print(
            f"[WARNING] Article website returned HTTP error: {e}"
        )

        return None


    # ======================================================
    # OTHER ERROR
    # ======================================================

    except Exception as e:

        print(
            f"[WARNING] Article extraction failed: {e}"
        )

        return None