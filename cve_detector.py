import re


# ==========================================
# CVE DETECTION
# ==========================================

def extract_cves(text):
    """
    Extract CVE identifiers from text.

    Example:
        CVE-2026-85046
        CVE-2026-67276

    Duplicate CVE identifiers are removed while
    preserving their original order.
    """

    if not text:
        return []


    # Standard CVE format:
    # CVE-YYYY-NNNN
    #
    # The final number can contain 4 or more digits.

    pattern = r"\bCVE-\d{4}-\d{4,}\b"


    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )


    # ------------------------------------------------------
    # Remove duplicates while preserving order
    # ------------------------------------------------------

    unique_cves = []

    seen = set()


    for cve in matches:

        cve = cve.upper()


        if cve not in seen:

            seen.add(cve)

            unique_cves.append(cve)


    return unique_cves


# ==========================================
# COMPATIBILITY FUNCTION
# ==========================================

def detect_cves(text):
    """
    Compatibility wrapper used by main.py.

    main.py calls detect_cves(), while the original
    detector function is extract_cves().
    """

    return extract_cves(text)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    sample_text = """

    Google disclosed CVE-2026-85046.

    MikroTik vulnerability CVE-2026-67276
    is being actively exploited.

    Another issue affects CVE-2025-55555.

    CVE-2026-85046 was mentioned again.

    """


    result = detect_cves(
        sample_text
    )


    print(
        "Detected CVEs:"
    )


    if result:

        for cve in result:

            print(
                cve
            )

    else:

        print(
            "No CVE detected."
        )