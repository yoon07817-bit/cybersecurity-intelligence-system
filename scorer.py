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
# Critical Keywords (Canonical -> Synonyms)
# ==========================================================

CRITICAL_KEYWORDS = {
    "zero-day": [
        "zero-day",
        "zero day",
        "0day",
    ],

    "actively exploited": [
        "actively exploited",
        "being exploited",
        "currently exploited",
        "confirmed exploitation",
        "under active attack",
        "ongoing attacks",
        "used in attacks",
        "attacks observed",
        "seen in the wild",
        "exploited in the wild",
        "mass exploitation",
    ],

    "ransomware": [
        "ransomware",
        "file-encrypting malware",
        "encrypting malware",
    ],

    "nation-state": [
        "nation-state",
        "state-sponsored",
        "government-backed",
        "apt",
        "advanced persistent threat",
    ],

    "critical infrastructure": [
        "critical infrastructure",
        "power grid",
        "water treatment",
        "energy sector",
        "healthcare system",
        "hospital network",
    ],

    "wormable": [
        "wormable",
        "self-propagating",
    ],

    "supply chain attack": [
        "supply chain attack",
        "software supply chain",
        "third-party compromise",
    ],

    "backdoor": [
        "backdoor",
        "hidden backdoor",
        "malicious backdoor",
    ],

    "privilege escalation": [
        "privilege escalation",
        "elevation of privilege",
    ],

    "sandbox escape": [
        "sandbox escape",
        "container escape",
    ],

    "remote takeover": [
        "remote takeover",
        "complete system compromise",
        "full system compromise",
    ],
}

# ==========================================================
# High Keywords
# ==========================================================

HIGH_KEYWORDS = {
    "cve": [
        "cve",
    ],

    "remote code execution": [
        "remote code execution",
        "rce",
        "execute arbitrary code",
        "arbitrary code execution",
    ],

    "authentication bypass": [
        "authentication bypass",
        "login bypass",
        "bypass authentication",
    ],

    "command injection": [
        "command injection",
        "os command injection",
    ],

    "sql injection": [
        "sql injection",
        "sqli",
    ],

    "data breach": [
        "data breach",
        "data leak",
        "information leak",
        "database leak",
        "customer data exposed",
        "sensitive data exposed",
    ],

    "credential theft": [
        "credential theft",
        "stolen credentials",
        "credential compromise",
        "password theft",
    ],

    "vulnerability": [
        "vulnerability",
        "security flaw",
        "security issue",
        "software flaw",
        "bug",
    ],

    "exploit": [
        "exploit",
        "exploitation",
        "exploit code",
    ],

    "patch": [
        "patch",
        "patched",
        "patches",
        "security update",
        "hotfix",
    ],

    "proof of concept": [
        "proof of concept",
        "poc",
    ],

    "denial of service": [
        "denial of service",
        "dos",
        "ddos",
        "distributed denial of service",
    ],

    "memory corruption": [
        "memory corruption",
        "buffer overflow",
        "heap overflow",
        "stack overflow",
        "use-after-free",
    ],
}

# ==========================================================
# Medium Keywords
# ==========================================================

MEDIUM_KEYWORDS = {
    "phishing": [
        "phishing",
        "email scam",
        "credential harvesting",
        "fake login",
        "fake login page",
        "phishing campaign",
    ],

    "malware": [
        "malware",
        "malicious software",
        "malicious program",
    ],

    "trojan": [
        "trojan",
        "trojan horse",
    ],

    "spyware": [
        "spyware",
        "surveillance malware",
    ],

    "adware": [
        "adware",
    ],

    "warning": [
        "warning",
        "alert",
        "caution",
    ],

    "advisory": [
        "advisory",
        "security advisory",
        "bulletin",
        "security bulletin",
    ],

    "update": [
        "update",
        "updated",
        "software update",
    ],

    "social engineering": [
        "social engineering",
        "human manipulation",
    ],

    "risk": [
        "risk",
        "security risk",
    ],

    "campaign": [
        "campaign",
        "malicious campaign",
        "attack campaign",
    ],
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
# Severity Promotion Thresholds
# ==========================================================

#
# Severity Rules:
#
# Critical:
# - Any Critical keyword found
# - OR total score >= 20
#
# High:
# - Any High keyword found
# - OR total score >= 10
#
# Medium:
# - Any Medium keyword found
# - OR score below High threshold
#
# Low:
# - No keywords detected
#
# Score Calculation:
# Critical keyword = 5 points
# High keyword     = 3 points
# Medium keyword   = 1 point
#
# Examples:
#
# 4 High keywords:
# 4 x 3 = 12 points -> High
#
# 7 High keywords:
# 7 x 3 = 21 points -> Critical
#
# 20 Medium keywords:
# 20 x 1 = 20 points -> Critical
#
# ==========================================================

PROMOTION_THRESHOLDS = {
    "critical": 20, # Score >= 20 becomes Critical
    "high": 10,# Score >= 10 becomes High
}


# ==========================================================
# Helper Function
# ==========================================================

import re

def find_keywords(text, keyword_dict):
    """
    Find matching canonical keywords using synonym lists.
    """

    text = text.lower()
    found = set()

    for canonical_keyword, synonyms in keyword_dict.items():

        for synonym in synonyms:

            pattern = r"\b" + re.escape(synonym.lower()) + r"\b"

            if re.search(pattern, text):
                found.add(canonical_keyword)
                break

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


    score = (
        len(critical_matches) * KEYWORD_POINTS["critical"]
        + len(high_matches) * KEYWORD_POINTS["high"]
        + len(medium_matches) * KEYWORD_POINTS["medium"]
    )


    # ------------------------------------------------------
    # Determine Severity
    # ------------------------------------------------------
    if critical_matches:
        severity = "Critical"

    elif score >= PROMOTION_THRESHOLDS["critical"]:
        severity = "Critical"

    elif high_matches:
        severity = "High"

    elif score >= PROMOTION_THRESHOLDS["high"]:
        severity = "High"

    elif medium_matches:
        severity = "Medium"

    else:
        severity = "Low"


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