"""
scorer.py

Rule-Based Severity Scoring System

Stage 1:
Determine the article severity based on the highest severity
keyword found.

Priority:
Critical > High > Medium > Low

Stage 2:
Calculate a numerical score for ranking articles
within the same severity level.

Critical keyword = 5 points
High keyword = 3 points
Medium keyword = 1 point
"""

# ==========================================================
# Keyword Lists
# ==========================================================

CRITICAL_KEYWORDS = {
    "zero-day",
    "actively exploited",
    "ransomware",
    "nation-state",
    "critical infrastructure",
}

HIGH_KEYWORDS = {
    "cve",
    "remote code execution",
    "data breach",
    "vulnerability",
    "patch",
}

MEDIUM_KEYWORDS = {
    "phishing",
    "malware",
    "advisory",
    "warning",
    "update",
}

# ==========================================================
# Point Values
# ==========================================================

KEYWORD_POINTS = {
    "critical": 5,
    "high": 3,
    "medium": 1,
}

# ==========================================================
# Helper Function
# ==========================================================

def find_keywords(text, keyword_set):
    """
    Find matching keywords in a text.

    Parameters
    ----------
    text : str
        Article title and summary.

    keyword_set : set
        Set of keywords to search.

    Returns
    -------
    set
        Matched keywords (duplicates removed).
    """

    text = text.lower()

    found = set()

    for keyword in keyword_set:
        if keyword.lower() in text:
            found.add(keyword)

    return found


# ==========================================================
# Main Scoring Function
# ==========================================================

def score_article(title, summary):
    """
    Analyse an article and return its severity,
    score, and matched keywords.
    """

    text = f"{title} {summary}"

    # Find keywords
    critical_matches = find_keywords(text, CRITICAL_KEYWORDS)
    high_matches = find_keywords(text, HIGH_KEYWORDS)
    medium_matches = find_keywords(text, MEDIUM_KEYWORDS)

    # ------------------------------------------------------
    # Stage 1 - Determine Severity
    # ------------------------------------------------------

    if critical_matches:
        severity = "Critical"

    elif high_matches:
        severity = "High"

    elif medium_matches:
        severity = "Medium"

    else:
        severity = "Low"

    # ------------------------------------------------------
    # Stage 2 - Calculate Score
    # ------------------------------------------------------

    score = (
        len(critical_matches) * KEYWORD_POINTS["critical"]
        + len(high_matches) * KEYWORD_POINTS["high"]
        + len(medium_matches) * KEYWORD_POINTS["medium"]
    )

    # ------------------------------------------------------
    # Return Result
    # ------------------------------------------------------

    return {
        "severity": severity,
        "score": score,
        "critical_keywords": sorted(critical_matches),
        "high_keywords": sorted(high_matches),
        "medium_keywords": sorted(medium_matches),
    }


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    article_title = (
        "Microsoft confirms actively exploited zero-day vulnerability"
    )

    article_summary = (
        "The zero-day vulnerability allows remote code execution. "
        "Microsoft released a security patch after ransomware attacks. "
        "Users are advised to update their systems immediately."
    )

    result = score_article(article_title, article_summary)

    print("=" * 50)
    print("Cybersecurity Article Analysis")
    print("=" * 50)

    print(f"Severity : {result['severity']}")
    print(f"Score    : {result['score']}")

    print("\nCritical Keywords")
    print("-----------------")
    if result["critical_keywords"]:
        for keyword in result["critical_keywords"]:
            print(f"• {keyword}")
    else:
        print("None")

    print("\nHigh Keywords")
    print("-------------")
    if result["high_keywords"]:
        for keyword in result["high_keywords"]:
            print(f"• {keyword}")
    else:
        print("None")

    print("\nMedium Keywords")
    print("---------------")
    if result["medium_keywords"]:
        for keyword in result["medium_keywords"]:
            print(f"• {keyword}")
    else:
        print("None")