"""
Rule-Based Cybersecurity Article Classification and Severity Scoring

The classifier uses:
1. Article title as the strongest evidence.
2. Article summary as supporting evidence.
3. Context-aware critical indicators to reduce false positives.

Severity:
Critical > High > Medium > Low

Score:
Critical keyword = 5 points
High keyword     = 3 points
Medium keyword   = 1 point

Special handling:
- SANS ISC Stormcast -> General Security / Low
- Strong vulnerability titles -> Vulnerability
- Regulatory/compliance articles are not automatically Critical
- Fraud / fake-shop / card-stealing activity -> Phishing
- Malware activity is prioritised when clearly indicated
"""

import re


# ==========================================================
# CATEGORY KEYWORDS
# ==========================================================

CATEGORY_KEYWORDS = {

    "Ransomware": [
        "ransomware",
        "ransom demand",
        "ransom payment",
        "ransom note",
        "encrypted files",
        "encrypting files",
        "file encryption",
        "encrypted data",
        "files encrypted",
        "file-encrypting malware",
    ],

    "Data Breach": [
        "data breach",
        "breach affecting",
        "breached database",
        "database breach",
        "data leak",
        "data leaked",
        "information leak",
        "database leak",
        "data exposure",
        "data exposed",
        "personal data exposed",
        "personal information exposed",
        "sensitive data exposed",
        "customer data exposed",
        "stolen data",
        "data stolen",
        "records exposed",
        "records stolen",
        "information exposed",
        "millions of records",
        "records compromised",
        "customer information stolen",
    ],

    "Phishing": [
        "phishing",
        "phishing campaign",
        "phishing attack",
        "phishing service",
        "phishing-as-a-service",
        "credential harvesting",
        "credential phishing",
        "fake login",
        "fake login page",
        "fake login portal",
        "email scam",
        "malicious email",
        "malicious emails",
        "vishing",
        "smishing",
        "help desk scam",
        "social engineering",
        "credential theft",
        "credential stealing",
        "fake shop",
        "fake shops",
        "fake store",
        "fake stores",
        "counterfeit shop",
        "counterfeit shops",
        "card stealing",
        "credit card theft",
        "payment card theft",
        "card credentials",
    ],

    "Malware": [
        "malware",
        "malicious software",
        "malicious program",
        "trojan",
        "trojan horse",
        "spyware",
        "surveillance malware",
        "infostealer",
        "information stealer",
        "information-stealing malware",
        "backdoor",
        "linux backdoor",
        "windows backdoor",
        "web shell",
        "webshell",
        "rootkit",
        "botnet",
        "malicious payload",
        "malicious payloads",
        "malicious code",
    ],

    "Vulnerability": [
        "vulnerability",
        "vulnerabilities",
        "security vulnerability",
        "security vulnerabilities",
        "security flaw",
        "security flaws",
        "software flaw",
        "software flaws",
        "zero-day",
        "zero day",
        "0-day",
        "0day",
        "actively exploited vulnerability",
        "remote code execution",
        "rce",
        "authentication bypass",
        "command injection",
        "sql injection",
        "sqli",
        "memory corruption",
        "buffer overflow",
        "heap overflow",
        "stack overflow",
        "use-after-free",
        "privilege escalation",
        "security patch",
        "patches vulnerability",
        "patches vulnerabilities",
    ],

    "AI Security": [
        "artificial intelligence security",
        "ai security",
        "ai model security",
        "ai system security",
        "ai agent security",
        "ai agent",
        "ai agents",
        "ai model",
        "ai models",
        "generative ai",
        "generative artificial intelligence",
        "large language model",
        "large language models",
        "llm",
        "llms",
        "prompt injection",
        "prompt attack",
        "ai attack",
        "ai attacks",
        "ai threat",
        "ai threats",
        "ai security risk",
        "machine learning security",
        "machine learning attack",
    ],

    "Privacy": [
        "privacy",
        "privacy risk",
        "privacy issue",
        "privacy violation",
        "privacy concern",
        "personal information",
        "personal data",
        "user data",
        "online tracking",
        "privacy protection",
        "privacy regulation",
        "privacy regulations",
        "hiv status data",
    ],

    "Compliance": [
        "compliance",
        "regulation",
        "regulations",
        "regulatory",
        "regulatory requirement",
        "regulatory requirements",
        "gdpr",
        "hipaa",
        "pci dss",
        "nist compliance",
        "security compliance",
        "compliance requirement",
        "compliance requirements",
        "audit requirement",
        "audit requirements",
        "cyber resilience act",
        "cyber resilience",
        "cra reporting",
    ],
}


# ==========================================================
# CATEGORY PRIORITY
# ==========================================================

CATEGORY_PRIORITY = [
    "Ransomware",
    "Data Breach",
    "Phishing",
    "Malware",
    "Vulnerability",
    "AI Security",
    "Privacy",
    "Compliance",
]


# ==========================================================
# STRONG VULNERABILITY TITLE INDICATORS
# ==========================================================

STRONG_VULNERABILITY_INDICATORS = [
    "zero-day",
    "zero day",
    "0-day",
    "0day",
    "actively exploited vulnerability",
    "remote code execution",
    "pre-auth rce",
    "authentication bypass",
    "command injection",
    "sql injection",
    "security vulnerability",
    "security flaw",
]


# ==========================================================
# CRITICAL TITLE INDICATORS
# ==========================================================

CRITICAL_TITLE_INDICATORS = [
    "zero-day",
    "zero day",
    "0-day",
    "0day",
    "actively exploited",
    "exploited in the wild",
    "exploited to deploy",
    "exploited to install",
    "ransomware",
    "remote takeover",
    "full system compromise",
    "complete system compromise",
    "sandbox escape",
]


# ==========================================================
# CRITICAL KEYWORDS
# ==========================================================

CRITICAL_KEYWORDS = {

    "zero-day": [
        "zero-day",
        "zero day",
        "0-day",
        "0day",
    ],

    "actively exploited": [
        "actively exploited",
        "being exploited",
        "currently exploited",
        "confirmed exploitation",
        "under active attack",
        "ongoing attacks",
        "exploited in the wild",
        "mass exploitation",
        "exploited to deploy",
        "exploited to install",
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
        "advanced persistent threat",
        "apt group",
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
        "third party compromise",
    ],

    "backdoor": [
        "backdoor",
        "hidden backdoor",
        "malicious backdoor",
        "linux backdoor",
        "windows backdoor",
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
        "remote system takeover",
    ],
}


# ==========================================================
# HIGH KEYWORDS
# ==========================================================

HIGH_KEYWORDS = {

    "cve": [
        "cve-",
        "cve ",
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
        "credential stealing",
    ],

    "vulnerability": [
        "vulnerability",
        "vulnerabilities",
        "security flaw",
        "security flaws",
        "security issue",
        "security issues",
        "software flaw",
        "bug",
        "bugs",
    ],

    "exploit": [
        "exploit",
        "exploitation",
        "exploit code",
        "exploited",
    ],

    "patch": [
        "patch",
        "patched",
        "patches",
        "security update",
        "security updates",
        "hotfix",
    ],

    "proof of concept": [
        "proof of concept",
        "poc",
        "proof-of-concept",
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
# MEDIUM KEYWORDS
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
        "security risks",
    ],

    "campaign": [
        "campaign",
        "malicious campaign",
        "attack campaign",
    ],
}


# ==========================================================
# POINT VALUES
# ==========================================================

KEYWORD_POINTS = {
    "critical": 5,
    "high": 3,
    "medium": 1,
}


# ==========================================================
# STORMCAST
# ==========================================================

def is_stormcast_article(title):

    title = (title or "").lower()

    return (
        "isc stormcast" in title
        or "stormcast for" in title
        or "stormcast" in title
    )


# ==========================================================
# REGULATORY / COMPLIANCE DETECTION
# ==========================================================

def is_regulatory_article(title):

    title = (title or "").lower()

    indicators = [
        "regulation",
        "regulations",
        "regulatory",
        "compliance",
        "cyber resilience act",
        "eu cra",
        "reporting requirement",
        "reporting requirements",
        "legal requirement",
        "legal requirements",
        "policy",
        "law",
    ]

    return any(
        indicator in title
        for indicator in indicators
    )


# ==========================================================
# KEYWORD MATCHING
# ==========================================================

def keyword_matches(text, synonym):

    text = (text or "").lower()

    synonym = (
        synonym or ""
    ).lower().strip()


    if synonym == "cve-":

        return bool(
            re.search(
                r"\bcve-\d{4}-\d{4,}\b",
                text,
                re.IGNORECASE
            )
        )


    if synonym == "cve ":

        return bool(
            re.search(
                r"\bcve[-\s]\d{4}[-\s]\d{4,}\b",
                text,
                re.IGNORECASE
            )
        )


    pattern = (
        r"(?<!\w)"
        + re.escape(synonym)
        + r"(?!\w)"
    )


    return bool(
        re.search(
            pattern,
            text,
            re.IGNORECASE
        )
    )


# ==========================================================
# FIND KEYWORDS
# ==========================================================

def find_keywords(text, keyword_dict):

    found = set()

    for canonical_keyword, synonyms in keyword_dict.items():

        for synonym in synonyms:

            if keyword_matches(
                text,
                synonym
            ):

                found.add(
                    canonical_keyword
                )

                break

    return found


# ==========================================================
# CATEGORY SCORES
# ==========================================================

def get_category_scores(text):

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword_matches(
                text,
                keyword
            ):

                word_count = len(
                    keyword.split()
                )

                if word_count >= 3:
                    score += 3

                elif word_count == 2:
                    score += 2

                else:
                    score += 1

        scores[category] = score

    return scores


# ==========================================================
# CATEGORY DETECTION
# ==========================================================

def detect_category(title, summary):

    title = title or ""
    summary = summary or ""

    title_lower = title.lower()


    # ------------------------------------------------------
    # Stormcast
    # ------------------------------------------------------

    if is_stormcast_article(title):

        return "General Security"


    # ------------------------------------------------------
    # Strong vulnerability title
    # ------------------------------------------------------

    for indicator in STRONG_VULNERABILITY_INDICATORS:

        if indicator in title_lower:

            return "Vulnerability"


    # ------------------------------------------------------
    # Strong ransomware title
    # ------------------------------------------------------

    if "ransomware" in title_lower:

        return "Ransomware"


    # ------------------------------------------------------
    # Strong data breach title
    # ------------------------------------------------------

    if (
        "data breach" in title_lower
        or "data leak" in title_lower
        or "database breach" in title_lower
    ):

        return "Data Breach"


    # ------------------------------------------------------
    # Strong phishing / fraud title
    # ------------------------------------------------------

    phishing_title_indicators = [

        "phishing",
        "phishing service",
        "fake shop",
        "fake shops",
        "fake store",
        "fake stores",
        "fraud network",
        "steal credit cards",
        "stealing credit cards",
        "credit card theft",
        "card credentials",
        "credential theft",

    ]


    if any(
        indicator in title_lower
        for indicator in phishing_title_indicators
    ):

        return "Phishing"


    # ------------------------------------------------------
    # Strong malware title
    # ------------------------------------------------------

    malware_title_indicators = [

        "malware",
        "trojan",
        "spyware",
        "infostealer",
        "information stealer",
        "backdoor",
        "rootkit",
        "botnet",

    ]


    if any(
        indicator in title_lower
        for indicator in malware_title_indicators
    ):

        return "Malware"


    # ------------------------------------------------------
    # AI title
    # ------------------------------------------------------

    if (
        re.search(
            r"\bai\b",
            title_lower
        )
        or "artificial intelligence" in title_lower
        or "machine learning" in title_lower
    ):

        return "AI Security"


    # ------------------------------------------------------
    # Privacy title
    # ------------------------------------------------------

    if any(
        indicator in title_lower
        for indicator in [
            "privacy",
            "privacy regulation",
            "data protection",
            "tracking",
        ]
    ):

        return "Privacy"


    # ------------------------------------------------------
    # Compliance title
    # ------------------------------------------------------

    if is_regulatory_article(title):

        return "Compliance"


    # ------------------------------------------------------
    # Use summary only as supporting evidence
    # ------------------------------------------------------

    title_scores = get_category_scores(
        title
    )

    summary_scores = get_category_scores(
        summary
    )


    combined_scores = {}


    for category in CATEGORY_KEYWORDS:

        combined_scores[category] = (

            title_scores.get(
                category,
                0
            ) * 5

            +

            summary_scores.get(
                category,
                0
            )

        )


    matched_categories = [

        category

        for category, score
        in combined_scores.items()

        if score > 0

    ]


    if not matched_categories:

        return "General Security"


    highest_score = max(

        combined_scores[category]

        for category in matched_categories

    )


    top_categories = [

        category

        for category in matched_categories

        if combined_scores[category]
        == highest_score

    ]


    for category in CATEGORY_PRIORITY:

        if category in top_categories:

            return category


    return top_categories[0]


# ==========================================================
# DETERMINE CRITICAL INDICATORS
# ==========================================================

def find_contextual_critical_matches(
    title,
    summary,
    category
):

    title = title or ""
    summary = summary or ""

    title_lower = title.lower()
    summary_lower = summary.lower()


    critical_matches = set()


    # ------------------------------------------------------
    # Critical title indicators
    # ------------------------------------------------------

    for indicator in CRITICAL_TITLE_INDICATORS:

        if indicator in title_lower:

            # Map indicator to canonical keyword

            if (
                "zero-day" in indicator
                or "zero day" in indicator
                or "0-day" in indicator
                or "0day" in indicator
            ):

                critical_matches.add(
                    "zero-day"
                )

            elif "ransomware" in indicator:

                critical_matches.add(
                    "ransomware"
                )

            elif "actively exploited" in indicator:

                critical_matches.add(
                    "actively exploited"
                )

            elif "exploited in the wild" in indicator:

                critical_matches.add(
                    "actively exploited"
                )

            elif "exploited to deploy" in indicator:

                critical_matches.add(
                    "actively exploited"
                )

            elif "exploited to install" in indicator:

                critical_matches.add(
                    "actively exploited"
                )

            elif "sandbox escape" in indicator:

                critical_matches.add(
                    "sandbox escape"
                )

            elif "remote takeover" in indicator:

                critical_matches.add(
                    "remote takeover"
                )

            elif (
                "system compromise" in indicator
            ):

                critical_matches.add(
                    "remote takeover"
                )


    # ------------------------------------------------------
    # Critical malware context
    #
    # A backdoor in the actual article can be serious,
    # but a generic mention of "backdoor" in a summary
    # should not automatically make an article Critical.
    # ------------------------------------------------------

    if category == "Malware":

        if any(
            phrase in title_lower
            for phrase in [
                "backdoor",
                "rootkit",
                "ransomware",
                "actively exploited",
            ]
        ):

            if "backdoor" in title_lower:

                critical_matches.add(
                    "backdoor"
                )


    # ------------------------------------------------------
    # Critical ransomware
    # ------------------------------------------------------

    if category == "Ransomware":

        if "ransomware" in title_lower:

            critical_matches.add(
                "ransomware"
            )


    # ------------------------------------------------------
    # Do NOT promote regulatory articles to Critical
    # merely because their summary mentions:
    #
    # "actively exploited vulnerabilities"
    #
    # Example:
    # EU Cyber Resilience Act
    # ------------------------------------------------------

    if is_regulatory_article(title):

        return set()


    # ------------------------------------------------------
    # Summary-based critical evidence
    #
    # Only use summary evidence when the title already
    # clearly indicates a security incident.
    # ------------------------------------------------------

    security_title_context = any(

        indicator in title_lower

        for indicator in [

            "vulnerability",
            "flaw",
            "exploit",
            "zero-day",
            "zero day",
            "rce",
            "ransomware",
            "backdoor",
            "rootkit",
            "malware",
            "attack",
            "breach",

        ]

    )


    if security_title_context:

        summary_critical = find_keywords(
            summary,
            CRITICAL_KEYWORDS
        )


        critical_matches.update(
            summary_critical
        )


    return critical_matches


# ==========================================================
# SCORE ARTICLE
# ==========================================================

def score_article(title, summary):

    title = title or ""
    summary = summary or ""


    # ------------------------------------------------------
    # Stormcast
    # ------------------------------------------------------

    if is_stormcast_article(title):

        return {

            "category":
                "General Security",

            "severity":
                "Low",

            "score":
                0,

            "critical_keywords":
                [],

            "high_keywords":
                [],

            "medium_keywords":
                [],

        }


    # ------------------------------------------------------
    # Category
    # ------------------------------------------------------

    category = detect_category(
        title,
        summary
    )


    # ------------------------------------------------------
    # Critical matches
    # ------------------------------------------------------

    critical_matches = (
        find_contextual_critical_matches(
            title,
            summary,
            category
        )
    )


    # ------------------------------------------------------
    # High / Medium matches
    # ------------------------------------------------------

    high_matches = find_keywords(
        f"{title} {summary}",
        HIGH_KEYWORDS
    )


    medium_matches = find_keywords(
        f"{title} {summary}",
        MEDIUM_KEYWORDS
    )


    # ------------------------------------------------------
    # Regulatory articles
    #
    # Do not let generic vulnerability terminology
    # in the summary create a high/critical threat.
    # ------------------------------------------------------

    if is_regulatory_article(title):

        high_matches = {
            keyword
            for keyword in high_matches
            if keyword in {
                "data breach",
                "credential theft",
            }
        }


        critical_matches = set()


    # ------------------------------------------------------
    # Score
    # ------------------------------------------------------

    score = (

        len(critical_matches)
        * KEYWORD_POINTS["critical"]

        +

        len(high_matches)
        * KEYWORD_POINTS["high"]

        +

        len(medium_matches)
        * KEYWORD_POINTS["medium"]

    )


    # ------------------------------------------------------
    # Severity
    # ------------------------------------------------------

    if critical_matches:

        severity = "Critical"


    elif category == "Ransomware" and (
        "ransomware" in title.lower()
    ):

        severity = "Critical"


    elif score >= 10:

        severity = "High"


    elif high_matches:

        severity = "High"


    elif medium_matches:

        severity = "Medium"


    else:

        severity = "Low"


    # ------------------------------------------------------
    # Regulatory articles should normally be
    # Compliance / Privacy rather than Critical.
    # ------------------------------------------------------

    if is_regulatory_article(title):

        if category == "Compliance":

            if score >= 3:

                severity = "Medium"

            else:

                severity = "Low"

        elif category == "Privacy":

            severity = "Medium"


    # ------------------------------------------------------
    # Return result
    # ------------------------------------------------------

    return {

        "category":
            category,

        "severity":
            severity,

        "score":
            score,

        "critical_keywords":
            sorted(
                critical_matches
            ),

        "high_keywords":
            sorted(
                high_matches
            ),

        "medium_keywords":
            sorted(
                medium_matches
            ),

    }


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    test_articles = [

        (
            "Microsoft confirms actively exploited zero-day vulnerability",
            "The zero-day vulnerability allows remote code execution. "
            "Microsoft released a security patch."
        ),

        (
            "Mathspace discloses data breach affecting over 1 million people",
            "Attackers stole personal data from more than one million "
            "people after compromising the organisation."
        ),

        (
            "BigBear Microsoft 365 phishing service bypassed MFA",
            "A phishing service is being used to steal Microsoft 365 "
            "credentials through fake login pages."
        ),

        (
            "Magento zero-day exploited to deploy Linux backdoor",
            "Attackers actively exploited a zero-day vulnerability "
            "to deploy a Linux backdoor."
        ),

        (
            "Ransomware attack encrypts company files",
            "Attackers encrypted company files and demanded a ransom payment."
        ),

        (
            "New AI agent security risks discovered",
            "Researchers discovered security risks affecting AI agents."
        ),

        (
            "New privacy regulations announced",
            "New privacy regulations require organisations to review "
            "their data protection practices."
        ),

        (
            "Critical MikroTik Vulnerability - Patch Now",
            "MikroTik released a security update addressing a "
            "vulnerability affecting its products."
        ),

        (
            "Adobe Patches Magento Zero-Day Exploited to Deploy Rust Backdoor",
            "Attackers actively exploited a zero-day vulnerability "
            "to deploy a Rust backdoor and PHP web shell."
        ),

        (
            "ISC Stormcast For Wednesday, September 9th, 2026",
            "This routine briefing contains general cybersecurity news."
        ),

        (
            "DoppelCart fraud network uses 119,000 fake shops to steal credit cards",
            "The fraud network uses fake online stores to steal payment "
            "card credentials from victims."
        ),

        (
            "The EU CRA's Real Question: What Shipped, and When Did You Know?",
            "The EU Cyber Resilience Act introduces reporting requirements "
            "for actively exploited vulnerabilities."
        ),

        (
            "Slim Spider Steals Crypto Custody Secrets From Brazilian Financial Institution",
            "The threat actor used malware and backdoors to steal cloud "
            "credentials and cryptocurrency secrets."
        ),
    ]


    print("=" * 60)

    print(
        "Cybersecurity Article Classification"
    )

    print("=" * 60)


    for title, summary in test_articles:

        result = score_article(
            title,
            summary
        )


        print()

        print(
            "Title:"
        )

        print(
            title
        )

        print(
            "Category :",
            result["category"]
        )

        print(
            "Severity :",
            result["severity"]
        )

        print(
            "Score    :",
            result["score"]
        )

        print(
            "Critical :",
            result["critical_keywords"]
        )

        print(
            "High     :",
            result["high_keywords"]
        )

        print(
            "Medium   :",
            result["medium_keywords"]
        )