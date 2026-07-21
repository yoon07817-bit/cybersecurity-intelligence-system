import sqlite3
from datetime import datetime, date


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

                created_at

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (

            article["title"],

            article["url"],

            article.get("source"),

            article.get("category"),

            article.get("published_date"),

            article.get("summary"),

            article.get("severity"),

            article.get("score"),

            datetime.now().isoformat()

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


    today = date.today().isoformat()


    cursor.execute("""
        SELECT *
        FROM articles
        WHERE created_at LIKE ?
        ORDER BY created_at DESC

    """, (today + "%",))


    rows = cursor.fetchall()


    conn.close()


    return rows



# TEST RUN
if __name__ == "__main__":

    create_table()

    print("Database ready.")