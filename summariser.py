import os
import time
import requests


# ==========================================================
# GROQ API CONFIGURATION
# ==========================================================

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Please set it as an environment variable."
    )


GROQ_API_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)

GROQ_MODEL = "openai/gpt-oss-120b"


# ==========================================================
# FALLBACK SUMMARY
# ==========================================================

def create_fallback_summary(title, text):

    if not text:
        text = title

    cleaned_text = " ".join(
        text.strip().split()
    )

    fallback_body = cleaned_text[:500]

    if len(cleaned_text) > 500:
        fallback_body += "..."

    return (
        "## **Main Point**\n"
        f"{title}\n\n"

        "## **Key Points**\n"
        f"- Article topic: {title}\n"
        "- Security-related information was identified "
        "from the available article content.\n"
        "- Further review may be required to determine "
        "the full impact.\n\n"

        "## **Summary**\n"
        f"{fallback_body}"
    )


# ==========================================================
# SUMMARIZE ARTICLE
# ==========================================================

def summarize(title, text):

    if not text or not text.strip():

        return (
            "## **Main Point**\n"
            f"{title}\n\n"

            "## **Key Points**\n"
            "- No article body was available.\n"
            "- The article title was retained for analysis.\n"
            "- Further investigation may be required.\n\n"

            "## **Summary**\n"
            "No article body text available to summarize."
        )


    # ======================================================
    # LIMIT INPUT SIZE
    # ======================================================

    article_text = text.strip()

    # Reduced from 12,000 to 7,000 characters
    # to reduce token usage.

    max_characters = 7000

    if len(article_text) > max_characters:

        article_text = (
            article_text[:max_characters]
            + "\n[Article content truncated]"
        )


    # ======================================================
    # PROMPT
    # ======================================================

    prompt = f"""
You are a cybersecurity analyst.

Summarize the following cybersecurity article.

Focus on:
- what happened
- who or what is affected
- why it matters
- important security implications

Mention a CVE identifier only if it is explicitly
present in the article. Never invent a CVE.

Use exactly this structure:

## **Main Point**
(One clear sentence)

## **Key Points**
- Point 1
- Point 2
- Point 3

## **Summary**
(2-3 short sentences)

Title:
{title}

Article:
{article_text}
"""


    # ======================================================
    # HEADERS
    # ======================================================

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


    # ======================================================
    # REQUEST DATA
    # ======================================================

    data = {

        "model": GROQ_MODEL,

        "messages": [

            {
                "role": "system",
                "content": (
                    "You are a professional cybersecurity "
                    "analyst. Produce concise and accurate "
                    "threat intelligence summaries."
                )
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        "temperature": 0.2,

        # Reduced output size
        "max_completion_tokens": 350

    }


    # ======================================================
    # RETRY CONFIGURATION
    # ======================================================

    max_retries = 2


    for attempt in range(max_retries + 1):

        try:

            response = requests.post(

                GROQ_API_URL,

                headers=headers,

                json=data,

                timeout=(10, 30)

            )


            # ==================================================
            # RATE LIMIT
            # ==================================================

            if response.status_code == 429:

                if attempt < max_retries:

                    # Wait before retrying
                    wait_time = 2 + (
                        attempt * 2
                    )

                    print(
                        f"[WARNING] Groq rate limit reached. "
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(
                        wait_time
                    )

                    continue


                print(
                    f"[WARNING] Groq rate limit still active "
                    f"after {max_retries} retries. "
                    f"Using fallback summary."
                )


                return create_fallback_summary(
                    title,
                    text
                )


            # ==================================================
            # OTHER HTTP ERRORS
            # ==================================================

            response.raise_for_status()


            # ==================================================
            # PARSE RESPONSE
            # ==================================================

            result = response.json()


            choices = result.get(
                "choices",
                []
            )


            if not choices:

                print(
                    "[WARNING] Groq returned no choices. "
                    "Using fallback summary."
                )


                return create_fallback_summary(
                    title,
                    text
                )


            message = choices[0].get(
                "message",
                {}
            )


            content = message.get(
                "content"
            )


            if not content:

                print(
                    "[WARNING] Groq returned an empty "
                    "summary. Using fallback."
                )


                return create_fallback_summary(
                    title,
                    text
                )


            # Small delay between successful requests
            time.sleep(1.5)


            return content.strip()


        # ======================================================
        # TIMEOUT
        # ======================================================

        except requests.exceptions.Timeout:

            if attempt < max_retries:

                print(
                    "[WARNING] Groq API timed out. "
                    "Retrying..."
                )

                time.sleep(2)

                continue


            print(
                f"[WARNING] Groq API timed out for "
                f"article: '{title[:60]}...'"
            )


            return create_fallback_summary(
                title,
                text
            )


        # ======================================================
        # CONNECTION ERROR
        # ======================================================

        except requests.exceptions.ConnectionError:

            if attempt < max_retries:

                print(
                    "[WARNING] Connection to Groq failed. "
                    "Retrying..."
                )

                time.sleep(2)

                continue


            print(
                f"[ERROR] Could not connect to Groq API "
                f"for article: '{title[:60]}...'"
            )


            return create_fallback_summary(
                title,
                text
            )


        # ======================================================
        # HTTP ERROR
        # ======================================================

        except requests.exceptions.HTTPError as e:

            status_code = (
                e.response.status_code
                if e.response is not None
                else "Unknown"
            )


            print(
                f"[ERROR] Groq API HTTP error "
                f"{status_code} for article: "
                f"'{title[:60]}...'"
            )


            if e.response is not None:

                try:

                    error_data = (
                        e.response.json()
                    )


                    error_message = (
                        error_data
                        .get("error", {})
                        .get("message")
                    )


                    if error_message:

                        print(
                            f"[Groq] {error_message}"
                        )


                except Exception:

                    pass


            return create_fallback_summary(
                title,
                text
            )


        # ======================================================
        # OTHER ERRORS
        # ======================================================

        except Exception as e:

            print(
                f"[ERROR] Failed to summarize article "
                f"'{title[:60]}...': {e}"
            )


            return create_fallback_summary(
                title,
                text
            )


    return create_fallback_summary(
        title,
        text
    )