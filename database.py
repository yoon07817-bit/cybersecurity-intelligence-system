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


# ==========================================
# CURRENT TIME
# ==========================================

def current_time():

    return datetime.now(
        ZoneInfo("Asia/Yangon")
    ).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )


# ==========================================
# DATABASE MIGRATION
# ==========================================

def migrate_database():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        # --------------------------------------
        # Check articles columns
        # --------------------------------------

        cursor.execute(
            "PRAGMA table_info(articles)"
        )

        article_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if article_columns:

            if "category" not in article_columns:

                cursor.execute(
                    """
                    ALTER TABLE articles
                    ADD COLUMN category TEXT
                    """
                )

            if "severity" not in article_columns:

                cursor.execute(
                    """
                    ALTER TABLE articles
                    ADD COLUMN severity TEXT
                    """
                )

            if "score" not in article_columns:

                cursor.execute(
                    """
                    ALTER TABLE articles
                    ADD COLUMN score INTEGER
                    """
                )

            if "alert_sent" not in article_columns:

                cursor.execute(
                    """
                    ALTER TABLE articles
                    ADD COLUMN alert_sent INTEGER DEFAULT 0
                    """
                )

            if "created_at" not in article_columns:

                cursor.execute(
                    """
                    ALTER TABLE articles
                    ADD COLUMN created_at TEXT
                    """
                )

        # --------------------------------------
        # Check users columns
        # --------------------------------------

        cursor.execute(
            "PRAGMA table_info(users)"
        )

        user_columns = [
            row["name"]
            for row in cursor.fetchall()
        ]

        if user_columns:

            if "receive_daily_digest" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN receive_daily_digest
                    INTEGER DEFAULT 1
                    """
                )

            if "receive_critical_alerts" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN receive_critical_alerts
                    INTEGER DEFAULT 1
                    """
                )

            if "minimum_severity" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN minimum_severity
                    TEXT DEFAULT 'Low'
                    """
                )

            if "created_at" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN created_at TEXT
                    """
                )

            if "last_login" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN last_login TEXT
                    """
                )

            if "login_count" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN login_count INTEGER DEFAULT 0
                    """
                )

            if "account_status" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN account_status
                    TEXT DEFAULT 'Active'
                    """
                )

            if "role" not in user_columns:

                cursor.execute(
                    """
                    ALTER TABLE users
                    ADD COLUMN role
                    TEXT DEFAULT 'User'
                    """
                )

        conn.commit()

    finally:

        conn.close()


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def create_table():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        # --------------------------------------
        # Articles
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS articles(

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
            """
        )

        # --------------------------------------
        # Users
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                email TEXT UNIQUE NOT NULL,

                password_hash TEXT NOT NULL,

                receive_daily_digest
                INTEGER DEFAULT 1,

                receive_critical_alerts
                INTEGER DEFAULT 1,

                minimum_severity
                TEXT DEFAULT 'Low',

                created_at TEXT,

                last_login TEXT,

                login_count
                INTEGER DEFAULT 0,

                account_status
                TEXT DEFAULT 'Active',

                role
                TEXT DEFAULT 'User'

            )
            """
        )

        # --------------------------------------
        # CVE Details
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cve_details(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                article_id INTEGER,

                cve_id TEXT,

                cvss_score REAL,

                severity TEXT,

                description TEXT,

                affected_product TEXT,

                created_at TEXT,

                FOREIGN KEY(article_id)
                REFERENCES articles(id)

            )
            """
        )

        # --------------------------------------
        # Recommendations
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                category TEXT,

                severity TEXT,

                advice TEXT

            )
            """
        )

        conn.commit()

    finally:

        conn.close()

    # Run migration after table creation
    migrate_database()


# ==========================================
# ARTICLE FUNCTIONS
# ==========================================

def insert_article(article):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT OR IGNORE INTO articles

            (
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

            VALUES(?,?,?,?,?,?,?,?,?)
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
                current_time()
            )
        )

        conn.commit()

        article_id = cursor.lastrowid

        # If INSERT OR IGNORE ignored the article,
        # lastrowid may not represent the existing row.
        if not article_id:

            cursor.execute(
                """
                SELECT id
                FROM articles
                WHERE url=?
                """,
                (article["url"],)
            )

            existing = cursor.fetchone()

            if existing:

                article_id = existing["id"]

        return article_id

    finally:

        conn.close()


def save_article(article):

    return insert_article(article)


def get_articles():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM articles
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def article_exists(url):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT id
            FROM articles
            WHERE url=?
            """,
            (url,)
        )

        result = cursor.fetchone()

        return result is not None

    finally:

        conn.close()


def get_critical_articles():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM articles
            WHERE severity='Critical'
            AND alert_sent=0
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def mark_alert_sent(article_id):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE articles
            SET alert_sent=1
            WHERE id=?
            """,
            (article_id,)
        )

        conn.commit()

    finally:

        conn.close()

# ==========================================
# CVE FUNCTIONS
# ==========================================

def save_cve(cve_data):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO cve_details

            (
                article_id,
                cve_id,
                cvss_score,
                severity,
                description,
                affected_product,
                created_at
            )

            VALUES(?,?,?,?,?,?,?)
            """,

            (
                cve_data["article_id"],
                cve_data["cve_id"],
                cve_data.get("cvss_score"),
                cve_data.get("severity"),
                cve_data.get("description"),
                cve_data.get("affected_product"),
                current_time()
            )
        )

        conn.commit()

    finally:

        conn.close()


def get_cve_by_article(article_id):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM cve_details
            WHERE article_id=?
            """,
            (article_id,)
        )

        return cursor.fetchall()

    finally:

        conn.close()


def get_all_cves():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM cve_details
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


# ==========================================
# PROTECTION RECOMMENDATION FUNCTIONS
# ==========================================

def save_recommendation(
    category,
    severity,
    advice
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO recommendations

            (
                category,
                severity,
                advice
            )

            VALUES(?,?,?)
            """,

            (
                category,
                severity,
                advice
            )
        )

        conn.commit()

    finally:

        conn.close()


def get_recommendation(
    category,
    severity
):
    """
    Protection recommendation search.

    Priority:

    1. Exact category + severity
    2. Category only
    3. Severity only
    4. General Security
    5. Built-in fallback
    """

    conn = create_connection()
    cursor = conn.cursor()

    try:

        # --------------------------------------
        # Exact category + severity
        # --------------------------------------

        cursor.execute(
            """
            SELECT advice
            FROM recommendations
            WHERE category=?
            AND severity=?
            LIMIT 1
            """,

            (
                category,
                severity
            )
        )

        result = cursor.fetchone()

        if result:

            return result["advice"]


        # --------------------------------------
        # Category fallback
        # --------------------------------------

        cursor.execute(
            """
            SELECT advice
            FROM recommendations
            WHERE category=?
            LIMIT 1
            """,

            (
                category,
            )
        )

        result = cursor.fetchone()

        if result:

            return result["advice"]


        # --------------------------------------
        # Severity fallback
        # --------------------------------------

        cursor.execute(
            """
            SELECT advice
            FROM recommendations
            WHERE severity=?
            LIMIT 1
            """,

            (
                severity,
            )
        )

        result = cursor.fetchone()

        if result:

            return result["advice"]


        # --------------------------------------
        # General Security
        # --------------------------------------

        cursor.execute(
            """
            SELECT advice
            FROM recommendations
            WHERE category='General Security'
            LIMIT 1
            """
        )

        result = cursor.fetchone()

        if result:

            return result["advice"]


    finally:

        conn.close()


    # ------------------------------------------
    # Final built-in fallback
    # ------------------------------------------

    fallback_recommendations = {

        "Ransomware":
            "Immediately isolate affected systems, "
            "restore from verified offline backups, "
            "remove the malware, patch vulnerable systems, "
            "and strengthen endpoint protection.",

        "Data Breach":
            "Identify and contain the affected systems, "
            "reset exposed credentials, review access "
            "controls, investigate the scope of exposure, "
            "and monitor for further misuse.",

        "Phishing":
            "Use phishing-resistant authentication, "
            "enable multi-factor authentication, "
            "train users to recognise suspicious messages, "
            "and verify links before entering credentials.",

        "Malware":
            "Isolate infected devices, remove malicious "
            "software, update security controls, scan "
            "affected systems, and monitor for persistence.",

        "Vulnerability":
            "Apply the vendor security patch as soon as "
            "possible, review affected systems, restrict "
            "exposure, and monitor for exploitation.",

        "AI Security":
            "Review AI system access controls, validate "
            "inputs and outputs, protect sensitive data, "
            "monitor AI activity, and apply appropriate "
            "AI security controls.",

        "Privacy":
            "Minimise unnecessary data collection, "
            "protect personal information, review access "
            "permissions, and apply appropriate privacy "
            "and data protection controls.",

        "Compliance":
            "Review applicable security requirements, "
            "maintain appropriate controls and records, "
            "perform regular audits, and address identified "
            "compliance gaps.",

        "General Security":
            "Maintain regular security updates, monitor "
            "threat intelligence sources, review access "
            "controls, and follow cybersecurity best practices."
    }


    return fallback_recommendations.get(
        category,
        fallback_recommendations[
            "General Security"
        ]
    )


# ==========================================
# USER FUNCTIONS
# ==========================================

def create_user(email, password):

    password_hash = generate_password_hash(password)

    conn = create_connection()

    try:

        cursor = conn.cursor()

        cursor.execute(
            """
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
            )
        )

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        conn.rollback()

        return False

    finally:

        conn.close()


# ==========================================
# LOGIN FUNCTION
# ==========================================

def check_login(
    email,
    password
):

    user = get_user_by_email(
        email
    )

    if user:

        if user["account_status"] != "Active":

            return None


        if check_password_hash(
            user["password_hash"],
            password
        ):

            return user


    return None

# ==========================================
# GET USER BY EMAIL
# ==========================================

def get_user_by_email(email):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (email,)
        )

        return cursor.fetchone()

    finally:

        conn.close()

# ==========================================
# GET USER BY ID
# ==========================================

def get_user_by_id(user_id):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            WHERE id=?
            """,
            (user_id,)
        )

        return cursor.fetchone()

    finally:

        conn.close()


# ==========================================
# VERIFY USER
# ==========================================

def verify_user(
    email,
    password
):
    """
    Verify login credentials.

    This function is used by dashboard/app.py.

    Returns:
        sqlite3.Row user record
        if credentials are valid.

        None if:
        - email does not exist
        - password is incorrect
        - account is disabled
    """

    user = get_user_by_email(
        email
    )


    # User does not exist
    if user is None:

        return None


    # Check account status
    if user["account_status"] != "Active":

        return None


    # Check password
    if check_password_hash(
        user["password_hash"],
        password
    ):

        return user


    return None


# ==========================================
# UPDATE LOGIN INFORMATION
# ==========================================

def update_login(
    user_id
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE users

            SET
                last_login=?,
                login_count=login_count+1

            WHERE id=?
            """,

            (
                current_time(),
                user_id
            )
        )

        conn.commit()

    finally:

        conn.close()

# ==========================================
# UPDATE LAST LOGIN
# ==========================================

def update_last_login(user_id):
    return update_login(user_id)        

# ==========================================
# ADMIN FUNCTIONS
# ==========================================

def get_all_users():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT *
            FROM users
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


def disable_user(
    user_id
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE users

            SET account_status='Disabled'

            WHERE id=?
            """,

            (
                user_id,
            )
        )

        conn.commit()

    finally:

        conn.close()


def enable_user(
    user_id
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE users

            SET account_status='Active'

            WHERE id=?
            """,

            (
                user_id,
            )
        )

        conn.commit()

    finally:

        conn.close()


def delete_user(
    user_id
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            DELETE FROM users
            WHERE id=?
            """,

            (
                user_id,
            )
        )

        conn.commit()

    finally:

        conn.close()


# ==========================================
# USER PREFERENCES
# ==========================================

def update_user_preferences(
    user_id,
    receive_daily_digest=None,
    receive_critical_alerts=None,
    minimum_severity=None
):

    conn = create_connection()
    cursor = conn.cursor()

    try:

        updates = []
        values = []


        if receive_daily_digest is not None:

            updates.append(
                "receive_daily_digest=?"
            )

            values.append(
                int(receive_daily_digest)
            )


        if receive_critical_alerts is not None:

            updates.append(
                "receive_critical_alerts=?"
            )

            values.append(
                int(receive_critical_alerts)
            )


        if minimum_severity is not None:

            updates.append(
                "minimum_severity=?"
            )

            values.append(
                minimum_severity
            )


        if not updates:

            return


        values.append(
            user_id
        )


        query = (
            "UPDATE users SET "
            + ", ".join(updates)
            + " WHERE id=?"
        )


        cursor.execute(
            query,
            values
        )


        conn.commit()

    finally:

        conn.close()


# ==========================================
# USER COUNT
# ==========================================

def get_user_count():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            AS count
            FROM users
            """
        )

        result = cursor.fetchone()

        return result["count"]

    finally:

        conn.close()


# ==========================================
# ARTICLE COUNT
# ==========================================

def get_article_count():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT COUNT(*)
            AS count
            FROM articles
            """
        )

        result = cursor.fetchone()

        return result["count"]

    finally:

        conn.close()


# ==========================================
# CATEGORY STATISTICS
# ==========================================

def get_category_counts():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                category,
                COUNT(*) AS count

            FROM articles

            GROUP BY category

            ORDER BY count DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()


# ==========================================
# SEVERITY STATISTICS
# ==========================================

def get_severity_counts():

    conn = create_connection()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT
                severity,
                COUNT(*) AS count

            FROM articles

            GROUP BY severity

            ORDER BY count DESC
            """
        )

        return cursor.fetchall()

    finally:

        conn.close()

# ==========================================
# GET USERS FOR EMAIL ALERTS
# ==========================================

def get_users_for_alert(alert_type="daily"):
    """
    Return active users who are subscribed
    to the requested email alert type.

    Supported alert types:
    - daily
    - weekly
    - critical
    """

    conn = create_connection()
    cursor = conn.cursor()

    try:

        # --------------------------------------
        # Daily digest subscribers
        # --------------------------------------

        if alert_type == "daily":

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE account_status='Active'
                AND receive_daily_digest=1
                """
            )


        # --------------------------------------
        # Weekly digest subscribers
        # --------------------------------------

        elif alert_type == "weekly":

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE account_status='Active'
                AND receive_daily_digest=1
                """
            )


        # --------------------------------------
        # Critical alert subscribers
        # --------------------------------------

        elif alert_type == "critical":

            cursor.execute(
                """
                SELECT *
                FROM users
                WHERE account_status='Active'
                AND receive_critical_alerts=1
                """
            )


        # --------------------------------------
        # Unknown alert type
        # --------------------------------------

        else:

            return []


        return cursor.fetchall()

    finally:

        conn.close()

# ==========================================
# INITIAL DATABASE SETUP
# ==========================================

create_table()


if __name__ == "__main__":

    print(
        "Database initialized successfully."
    )