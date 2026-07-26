import sqlite3

from datetime import datetime
from zoneinfo import ZoneInfo


DB_NAME = "save_data.db"



# CONNECTION
def create_connection():

    return sqlite3.connect(DB_NAME)





# TABLE SETUP
def create_table():

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            url TEXT UNIQUE NOT NULL,

            source TEXT,

            category TEXT,

            published_date TEXT,

            summary TEXT,

            severity TEXT,

            score INTEGER,

            alert_sent INTEGER DEFAULT 0,

            created_at TEXT

        )
    """)


    conn.commit()

    conn.close()





# SAVE ARTICLE
def save_article(article):

    conn = create_connection()

    cursor = conn.cursor()


    try:

        cursor.execute("""

            INSERT INTO articles (

                title,

                url,

                source,

                category,

                published_date,

                summary,

                severity,

                score,

                alert_sent,

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (

            article["title"],

            article["url"],

            article.get("source"),

            article.get("category"),

            article.get("published_date"),

            article.get("summary"),

            article.get("severity"),

            article.get("score"),

            0,

            datetime.now(
                ZoneInfo("Asia/Yangon")
            ).strftime(
                "%Y-%m-%d %H:%M:%S MMT"
            )

        ))


        conn.commit()



    except sqlite3.IntegrityError:

        print(
            "Duplicate article skipped:",
            article["title"]
        )



    finally:

        conn.close()





# CHECK IF ARTICLE EXISTS
def article_exists(url):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute(

        "SELECT 1 FROM articles WHERE url = ?",

        (url,)

    )


    result = cursor.fetchone()


    conn.close()


    return result is not None





# GET TODAY'S ARTICLES
def get_articles_today():

    conn = create_connection()

    cursor = conn.cursor()


    today = datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime("%Y-%m-%d")


    cursor.execute("""

        SELECT *

        FROM articles

        WHERE created_at LIKE ?

        ORDER BY created_at DESC

    """,

    (today + "%",))


    rows = cursor.fetchall()


    conn.close()


    return rows





# GET NEW CRITICAL ARTICLES
# Used by Week 13 Alert System
def get_critical_articles():

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute("""

        SELECT

            id,

            title,

            url,

            summary,

            severity,

            score

        FROM articles

        WHERE severity = 'Critical'

        AND alert_sent = 0

        ORDER BY created_at DESC

    """)


    rows = cursor.fetchall()


    conn.close()



    articles = []


    for row in rows:


        articles.append({

            "id": row[0],

            "title": row[1],

            "link": row[2],

            "summary": row[3],

            "severity": row[4],

            "score": row[5]

        })


    return articles





# MARK ALERT AS SENT
# Prevents duplicate alert emails
def mark_alert_sent(article_id):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute("""

        UPDATE articles

        SET alert_sent = 1

        WHERE id = ?

    """,

    (article_id,))


    conn.commit()

    conn.close()





# TEST RUN
if __name__ == "__main__":

    create_table()

    print(
        "Database ready."
    )