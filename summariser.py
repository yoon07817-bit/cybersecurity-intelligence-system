import os
import requests


API_KEY = os.getenv("GROQ_API_KEY")


if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set."
    )


def summarize(text):

    prompt = f"""
Summarize the following cybersecurity article using Markdown formatting.

Requirements:
- Use clear section headings (##).
- Bold important information using **bold**.
- Use bullet points for key information.
- Keep the summary concise.

Format:

## **Main Point**
(One sentence)

## **Key Points**
- Point 1
- Point 2
- Point 3

## **Summary**
(2-3 sentences)

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


    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=60
    )


    response.raise_for_status()


    result = response.json()


    return result["choices"][0]["message"]["content"]