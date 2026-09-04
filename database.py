import os
import sqlite3

from datetime import datetime
from zoneinfo import ZoneInfo

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# ==========================================
# DATABASE LOCATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_NAME = os.path.join(
    BASE_DIR,
    "save_data.db"
)



# ==========================================
# DATABASE CONNECTION
# ==========================================

def create_connection():

    conn = sqlite3.connect(
        DB_NAME,
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    return conn



def current_time():

    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )



# ==========================================
# CREATE TABLES
# ==========================================

def create_table():

    conn = create_connection()

    cursor = conn.cursor()



    # ARTICLES

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



    # USERS

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            email TEXT UNIQUE NOT NULL,

            password_hash TEXT NOT NULL,


            receive_daily_digest INTEGER DEFAULT 1,

            receive_critical_alerts INTEGER DEFAULT 1,


            minimum_severity TEXT DEFAULT 'Low',


            created_at TEXT,

            last_login TEXT,

            login_count INTEGER DEFAULT 0,


            account_status TEXT DEFAULT 'Active',

            role TEXT DEFAULT 'User'

        )
    """)



    conn.commit()

    conn.close()


    migrate_database()





# ==========================================
# DATABASE MIGRATION
# ==========================================

def migrate_database():

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute(
        "PRAGMA table_info(users)"
    )


    columns = [

        row["name"]

        for row in cursor.fetchall()

    ]



    new_columns = {


        "minimum_severity":
        "TEXT DEFAULT 'Low'",


        "role":
        "TEXT DEFAULT 'User'"


    }



    for column, datatype in new_columns.items():


        if column not in columns:


            cursor.execute(
                f"""
                ALTER TABLE users
                ADD COLUMN {column} {datatype}
                """
            )



    conn.commit()

    conn.close()





# ==========================================
# ARTICLE FUNCTIONS
# ==========================================


def save_article(article):

    conn = create_connection()

    cursor = conn.cursor()


    try:

        cursor.execute("""
            INSERT INTO articles

            (
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

            current_time()

        ))



        conn.commit()



    except sqlite3.IntegrityError:


        print(
            "Duplicate article skipped:",
            article["title"]
        )



    finally:

        conn.close()





def get_critical_articles():

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *

        FROM articles

        WHERE severity='Critical'

        AND alert_sent=0

        ORDER BY created_at DESC

    """)



    rows = cursor.fetchall()


    conn.close()



    return [

        dict(row)

        for row in rows

    ]







def mark_alert_sent(article_id):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute("""
        UPDATE articles

        SET alert_sent=1

        WHERE id=?

    """,

    (

        article_id,

    ))



    conn.commit()

    conn.close()

def article_exists(url):

    conn = create_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT 1

        FROM articles

        WHERE url = ?

    """,
    (
        url,
    ))


    result = cursor.fetchone()


    conn.close()


    return result is not None




# ==========================================
# USER FUNCTIONS
# ==========================================


def create_user(email, password):

    conn = create_connection()

    cursor = conn.cursor()



    password_hash = generate_password_hash(
        password
    )



    try:

        cursor.execute("""
            INSERT INTO users

            (
                email,
                password_hash,
                created_at
            )

            VALUES (?, ?, ?)

        """,

        (

            email,

            password_hash,

            current_time()

        ))



        conn.commit()


        return True



    except sqlite3.IntegrityError:


        return False



    finally:

        conn.close()





def get_user_by_email(email):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *

        FROM users

        WHERE email=?

    """,

    (

        email,

    ))



    user = cursor.fetchone()


    conn.close()


    return user





def get_user_by_id(user_id):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *

        FROM users

        WHERE id=?

    """,

    (

        user_id,

    ))



    user = cursor.fetchone()


    conn.close()


    return user





def verify_user(email, password):

    user = get_user_by_email(email)



    if user:


        if user["account_status"] == "Disabled":

            return None



        if check_password_hash(

            user["password_hash"],

            password

        ):

            return user



    return None






# ==========================================
# LOGIN TRACKING
# ==========================================


def update_last_login(user_id):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        UPDATE users

        SET

        last_login=?,

        login_count=login_count+1


        WHERE id=?

    """,

    (

        current_time(),

        user_id

    ))



    conn.commit()

    conn.close()






# ==========================================
# USER SETTINGS
# ==========================================


def update_user_preferences(

        user_id,

        daily,

        critical,

        severity

):


    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        UPDATE users

        SET

        receive_daily_digest=?,

        receive_critical_alerts=?,

        minimum_severity=?


        WHERE id=?

    """,

    (

        daily,

        critical,

        severity,

        user_id

    ))



    conn.commit()

    conn.close()






# ==========================================
# ADMIN MANAGEMENT
# ==========================================


def get_all_users():

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        SELECT *

        FROM users

        ORDER BY id DESC

    """)



    users = cursor.fetchall()


    conn.close()


    return users





def disable_user(user_id):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        UPDATE users

        SET

        account_status='Disabled',

        receive_daily_digest=0,

        receive_critical_alerts=0


        WHERE id=?

    """,

    (

        user_id,

    ))



    conn.commit()

    conn.close()





def enable_user(user_id):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        UPDATE users

        SET

        account_status='Active',

        receive_daily_digest=1,

        receive_critical_alerts=1


        WHERE id=?

    """,

    (

        user_id,

    ))



    conn.commit()

    conn.close()





def delete_user(user_id):

    conn = create_connection()

    cursor = conn.cursor()



    cursor.execute("""
        DELETE FROM users

        WHERE id=?

    """,

    (

        user_id,

    ))



    conn.commit()

    conn.close()






# ==========================================
# EMAIL SUBSCRIBERS
# ==========================================


def get_users_for_alert(alert_type="daily"):


    conn = create_connection()

    cursor = conn.cursor()



    if alert_type == "critical":


        cursor.execute("""
            SELECT email, minimum_severity

            FROM users

            WHERE receive_critical_alerts=1

            AND account_status='Active'

        """)



    else:


        cursor.execute("""
            SELECT email, minimum_severity

            FROM users

            WHERE receive_daily_digest=1

            AND account_status='Active'

        """)



    users = cursor.fetchall()


    conn.close()


    return users





# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    create_table()

    print(
        "Database and tables initialized successfully."
    )