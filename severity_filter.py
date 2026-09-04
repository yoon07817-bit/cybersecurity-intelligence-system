# ==========================================
# SEVERITY FILTER SYSTEM
# ==========================================


SEVERITY_LEVELS = {

    "Low": 1,

    "Medium": 2,

    "High": 3,

    "Critical": 4

}



def allow_alert(article_severity, user_threshold):

    """
    Checks whether an article severity
    matches user's minimum severity preference.
    """


    article_level = SEVERITY_LEVELS.get(
        article_severity,
        0
    )


    user_level = SEVERITY_LEVELS.get(
        user_threshold,
        1
    )


    return article_level >= user_level