import os
import time
import requests

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. Please set it as an environment variable in your .env file."
    )


def summarize(title, text):
    """
    Generate a cybersecurity summary using Groq AI with strict timeout handling.
    """
    if not text or len(text.strip()) == 0:
        return f"## **Main Point**\n{title}\n\n## **Summary**\nNo article body text available to summarize."

    prompt = f"""
You are a cybersecurity analyst.

Summarize the following cybersecurity article using Markdown.

Requirements:
- Focus on what happened, who is affected, and why it matters.
- Keep the summary concise.
- Use the following format exactly.

## **Main Point**
(One sentence)

## **Key Points**
- Point 1
- Point 2
- Point 3

## **Summary**
(2-3 short sentences)

Title:
{title}

Article:
{text}
"""

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3
    }

    try:
        # timeout=(connect_timeout, read_timeout)
        # Prevents long hangs if network socket drops or API stalls
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=(5, 20)
        )

        response.raise_for_status()
        result = response.json()

        # Brief pause for rate-limiting compliance
        time.sleep(0.5)

        return result["choices"][0]["message"]["content"].strip()

    except requests.exceptions.Timeout:
        print(f"[WARNING] Groq API timed out for article: '{title[:40]}...'. Using fallback excerpt.")
        fallback_body = text[:300].strip() + "..." if text else title
        return f"## **Main Point**\n{title}\n\n## **Summary**\n{fallback_body}"

    except Exception as e:
        print(f"[ERROR] Failed to summarize article '{title[:40]}...': {e}")
        fallback_body = text[:300].strip() + "..." if text else title
        return f"## **Main Point**\n{title}\n\n## **Summary**\n{fallback_body}"