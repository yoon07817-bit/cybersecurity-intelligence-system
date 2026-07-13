import os
import time
import requests

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. Please set it as an environment variable."
    )


def summarize(title, text):
    """
    Generate a cybersecurity summary using Groq AI.
    """

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

        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        # Rate limiting
        time.sleep(1)

        return result["choices"][0]["message"]["content"].strip()

    except Exception as e:

        print(f"[ERROR] Failed to summarize article: {e}")

        return "Summary unavailable due to API error."