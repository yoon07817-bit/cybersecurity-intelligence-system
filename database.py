import os
import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from werkzeug.security import generate_password_hash, check_password_hash

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None


# ==========================================
# DATABASE CONFIGURATION
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "save_data.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
USE_POSTGRES = bool(DATABASE_URL)


# ==========================================
# DATABASE CONNECTION
# ==========================================
def create_connection():
    """Return a connection to Render PostgreSQL when DATABASE_URL exists;
    otherwise return the local SQLite connection.
    """
    if USE_POSTGRES:
        if psycopg2 is None:
            raise RuntimeError(
                "psycopg2 is required when DATABASE_URL is configured. "
                "Install psycopg2-binary."
            )
        return psycopg2.connect(DATABASE_URL, connect_timeout=15)

    conn = sqlite3.connect(DB_NAME, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


class DBConnection:
    """Small compatibility wrapper so the rest of this module can use
    SQLite-style '?' placeholders with both SQLite and PostgreSQL.
    """
    def __init__(self, conn):
        self.conn = conn

    def cursor(self):
        if USE_POSTGRES:
            return self.conn.cursor(cursor_factory=RealDictCursor)
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def db_connection():
    return DBConnection(create_connection())


def execute(cursor, query, params=None):
    """Execute SQL using '?' placeholders for both database engines."""
    if USE_POSTGRES:
        query = query.replace("?", "%s")
    if params is None:
        return cursor.execute(query)
    return cursor.execute(query, params)


# ==========================================
# CURRENT TIME
# ==========================================
def current_time():
    return datetime.now(ZoneInfo("Asia/Yangon")).strftime(
        "%Y-%m-%d %H:%M:%S MMT"
    )


# ==========================================
# CREATE / MIGRATE DATABASE TABLES
# ==========================================
def create_table():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        if USE_POSTGRES:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    source TEXT,
                    category TEXT,
                    published_date TEXT,
                    summary TEXT,
                    severity TEXT,
                    score INTEGER,
                    created_at TEXT,
                    alert_sent INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    receive_daily_digest INTEGER DEFAULT 1,
                    receive_critical_alerts INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    account_status TEXT DEFAULT 'Active',
                    role TEXT DEFAULT 'User',
                    receive_weekly_digest INTEGER DEFAULT 0,
                    minimum_severity TEXT DEFAULT 'Low'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cve_details (
                    id SERIAL PRIMARY KEY,
                    article_id INTEGER,
                    cve_id TEXT,
                    cvss_score REAL,
                    severity TEXT,
                    description TEXT,
                    affected_product TEXT,
                    created_at TEXT,
                    FOREIGN KEY (article_id) REFERENCES articles(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id SERIAL PRIMARY KEY,
                    category TEXT,
                    severity TEXT,
                    advice TEXT
                )
            """)
        else:
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
                    created_at TEXT,
                    alert_sent INTEGER DEFAULT 0
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    receive_daily_digest INTEGER DEFAULT 1,
                    receive_critical_alerts INTEGER DEFAULT 1,
                    created_at TEXT,
                    last_login TEXT,
                    login_count INTEGER DEFAULT 0,
                    account_status TEXT DEFAULT 'Active',
                    role TEXT DEFAULT 'User',
                    receive_weekly_digest INTEGER DEFAULT 0,
                    minimum_severity TEXT DEFAULT 'Low'
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cve_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    cve_id TEXT,
                    cvss_score REAL,
                    severity TEXT,
                    description TEXT,
                    affected_product TEXT,
                    created_at TEXT,
                    FOREIGN KEY (article_id) REFERENCES articles(id)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT,
                    severity TEXT,
                    advice TEXT
                )
            """)

            migrate_database(conn, cursor)

        conn.commit()
    finally:
        conn.close()


def migrate_database(conn=None, cursor=None):
    """Add columns used by the application to an older local SQLite DB.
    PostgreSQL databases created by create_table already contain all columns.
    """
    own_connection = conn is None
    if own_connection:
        conn = db_connection()
        cursor = conn.cursor()

    try:
        if USE_POSTGRES:
            # Safe for an older PostgreSQL database as well.
            statements = [
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS category TEXT",
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS severity TEXT",
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS score INTEGER",
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS created_at TEXT",
                "ALTER TABLE articles ADD COLUMN IF NOT EXISTS alert_sent INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS receive_daily_digest INTEGER DEFAULT 1",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS receive_critical_alerts INTEGER DEFAULT 1",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TEXT",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TEXT",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS login_count INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS account_status TEXT DEFAULT 'Active'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'User'",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS receive_weekly_digest INTEGER DEFAULT 0",
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS minimum_severity TEXT DEFAULT 'Low'",
            ]
            for statement in statements:
                cursor.execute(statement)
        else:
            cursor.execute("PRAGMA table_info(articles)")
            article_columns = [row["name"] for row in cursor.fetchall()]
            article_additions = {
                "category": "ALTER TABLE articles ADD COLUMN category TEXT",
                "severity": "ALTER TABLE articles ADD COLUMN severity TEXT",
                "score": "ALTER TABLE articles ADD COLUMN score INTEGER",
                "created_at": "ALTER TABLE articles ADD COLUMN created_at TEXT",
                "alert_sent": "ALTER TABLE articles ADD COLUMN alert_sent INTEGER DEFAULT 0",
            }
            for column, statement in article_additions.items():
                if article_columns and column not in article_columns:
                    cursor.execute(statement)

            cursor.execute("PRAGMA table_info(users)")
            user_columns = [row["name"] for row in cursor.fetchall()]
            user_additions = {
                "receive_daily_digest": "ALTER TABLE users ADD COLUMN receive_daily_digest INTEGER DEFAULT 1",
                "receive_critical_alerts": "ALTER TABLE users ADD COLUMN receive_critical_alerts INTEGER DEFAULT 1",
                "created_at": "ALTER TABLE users ADD COLUMN created_at TEXT",
                "last_login": "ALTER TABLE users ADD COLUMN last_login TEXT",
                "login_count": "ALTER TABLE users ADD COLUMN login_count INTEGER DEFAULT 0",
                "account_status": "ALTER TABLE users ADD COLUMN account_status TEXT DEFAULT 'Active'",
                "role": "ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'User'",
                "receive_weekly_digest": "ALTER TABLE users ADD COLUMN receive_weekly_digest INTEGER DEFAULT 0",
                "minimum_severity": "ALTER TABLE users ADD COLUMN minimum_severity TEXT DEFAULT 'Low'",
            }
            for column, statement in user_additions.items():
                if user_columns and column not in user_columns:
                    cursor.execute(statement)

        conn.commit()
    finally:
        if own_connection:
            conn.close()


# ==========================================
# ARTICLE FUNCTIONS
# ==========================================
def insert_article(article):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        if USE_POSTGRES:
            execute(cursor, """
                INSERT INTO articles
                (title, url, source, category, published_date, summary, severity, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (url) DO NOTHING
            """, (
                article["title"], article["url"], article.get("source"),
                article.get("category"), article.get("published_date"),
                article.get("summary"), article.get("severity"),
                article.get("score"), current_time()
            ))
        else:
            execute(cursor, """
                INSERT OR IGNORE INTO articles
                (title, url, source, category, published_date, summary, severity, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article["title"], article["url"], article.get("source"),
                article.get("category"), article.get("published_date"),
                article.get("summary"), article.get("severity"),
                article.get("score"), current_time()
            ))
        conn.commit()
        execute(cursor, "SELECT id FROM articles WHERE url=?", (article["url"],))
        row = cursor.fetchone()
        return row["id"] if row else None
    finally:
        conn.close()


def save_article(article):
    return insert_article(article)


def get_articles():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM articles ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


def article_exists(url):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT id FROM articles WHERE url=?", (url,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def get_critical_articles():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            SELECT * FROM articles
            WHERE severity='Critical' AND alert_sent=0
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def mark_alert_sent(article_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "UPDATE articles SET alert_sent=1 WHERE id=?", (article_id,))
        conn.commit()
    finally:
        conn.close()


# ==========================================
# CVE FUNCTIONS
# ==========================================
def save_cve(cve_data):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            INSERT INTO cve_details
            (article_id, cve_id, cvss_score, severity, description, affected_product, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            cve_data["article_id"], cve_data["cve_id"],
            cve_data.get("cvss_score"), cve_data.get("severity"),
            cve_data.get("description"), cve_data.get("affected_product"),
            current_time()
        ))
        conn.commit()
    finally:
        conn.close()


def get_cve_by_article(article_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM cve_details WHERE article_id=?", (article_id,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_cves():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM cve_details ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


# ==========================================
# PROTECTION RECOMMENDATION FUNCTIONS
# ==========================================
def save_recommendation(category, severity, advice):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            INSERT INTO recommendations (category, severity, advice)
            VALUES (?, ?, ?)
        """, (category, severity, advice))
        conn.commit()
    finally:
        conn.close()


def get_recommendation(category, severity):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            SELECT advice FROM recommendations
            WHERE category=? AND severity=? LIMIT 1
        """, (category, severity))
        result = cursor.fetchone()
        if result:
            return result["advice"]

        execute(cursor, """
            SELECT advice FROM recommendations
            WHERE category=? LIMIT 1
        """, (category,))
        result = cursor.fetchone()
        if result:
            return result["advice"]

        execute(cursor, """
            SELECT advice FROM recommendations
            WHERE severity=? LIMIT 1
        """, (severity,))
        result = cursor.fetchone()
        if result:
            return result["advice"]

        execute(cursor, """
            SELECT advice FROM recommendations
            WHERE category='General Security' LIMIT 1
        """)
        result = cursor.fetchone()
        if result:
            return result["advice"]
    finally:
        conn.close()

    fallback_recommendations = {
        "Ransomware": "Immediately isolate affected systems, restore from verified offline backups, remove the malware, patch vulnerable systems, and strengthen endpoint protection.",
        "Data Breach": "Identify and contain the affected systems, reset exposed credentials, review access controls, investigate the scope of exposure, and monitor for further misuse.",
        "Phishing": "Use phishing-resistant authentication, enable multi-factor authentication, train users to recognise suspicious messages, and verify links before entering credentials.",
        "Malware": "Isolate infected devices, remove malicious software, update security controls, scan affected systems, and monitor for persistence.",
        "Vulnerability": "Apply the vendor security patch as soon as possible, review affected systems, restrict exposure, and monitor for exploitation.",
        "AI Security": "Review AI system access controls, validate inputs and outputs, protect sensitive data, monitor AI activity, and apply appropriate AI security controls.",
        "Privacy": "Minimise unnecessary data collection, protect personal information, review access permissions, and apply appropriate privacy and data protection controls.",
        "Compliance": "Review applicable security requirements, maintain appropriate controls and records, perform regular audits, and address identified compliance gaps.",
        "General Security": "Maintain regular security updates, monitor threat intelligence sources, review access controls, and follow cybersecurity best practices."
    }
    return fallback_recommendations.get(category, fallback_recommendations["General Security"])


# ==========================================
# USER FUNCTIONS
# ==========================================
def create_user(email, password):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        execute(cursor, """
            INSERT INTO users (email, password_hash, created_at)
            VALUES (?, ?, ?)
        """, (email, password_hash, current_time()))
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_by_email(email):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM users WHERE email=?", (email,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Return one user by ID. Used by Flask-Login user_loader."""
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM users WHERE id=?", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()


# ==========================================
# LOGIN FUNCTIONS
# ==========================================
def check_login(email, password):
    user = get_user_by_email(email)
    if user is None:
        return None
    if user["account_status"] != "Active":
        return None
    if check_password_hash(user["password_hash"], password):
        return user
    return None


def verify_user(email, password):
    return check_login(email, password)


def update_login(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            UPDATE users
            SET last_login=?, login_count=login_count+1
            WHERE id=?
        """, (current_time(), user_id))
        conn.commit()
    finally:
        conn.close()


def update_last_login(user_id):
    return update_login(user_id)


# ==========================================
# ADMIN FUNCTIONS
# ==========================================
def get_all_users():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT * FROM users ORDER BY id DESC")
        return cursor.fetchall()
    finally:
        conn.close()


def disable_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "UPDATE users SET account_status='Disabled' WHERE id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def enable_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "UPDATE users SET account_status='Active' WHERE id=?", (user_id,))
        conn.commit()
    finally:
        conn.close()


def delete_user(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "DELETE FROM users WHERE id=?", (user_id,))
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
    conn = db_connection()
    cursor = conn.cursor()
    try:
        updates = []
        values = []

        if receive_daily_digest is not None:
            updates.append("receive_daily_digest=?")
            values.append(int(receive_daily_digest))
        if receive_critical_alerts is not None:
            updates.append("receive_critical_alerts=?")
            values.append(int(receive_critical_alerts))
        if minimum_severity is not None:
            updates.append("minimum_severity=?")
            values.append(minimum_severity)

        if not updates:
            return

        values.append(user_id)
        execute(
            cursor,
            "UPDATE users SET " + ", ".join(updates) + " WHERE id=?",
            values
        )
        conn.commit()
    finally:
        conn.close()


# ==========================================
# COUNTS / STATISTICS
# ==========================================
def get_user_count():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT COUNT(*) AS count FROM users")
        return cursor.fetchone()["count"]
    finally:
        conn.close()


def get_article_count():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, "SELECT COUNT(*) AS count FROM articles")
        return cursor.fetchone()["count"]
    finally:
        conn.close()


def get_category_counts():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            SELECT category, COUNT(*) AS count
            FROM articles
            GROUP BY category
            ORDER BY count DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def get_severity_counts():
    conn = db_connection()
    cursor = conn.cursor()
    try:
        execute(cursor, """
            SELECT severity, COUNT(*) AS count
            FROM articles
            GROUP BY severity
            ORDER BY count DESC
        """)
        return cursor.fetchall()
    finally:
        conn.close()


# ==========================================
# EMAIL SUBSCRIBERS
# ==========================================
def get_users_for_alert(alert_type="daily"):
    conn = db_connection()
    cursor = conn.cursor()
    try:
        if alert_type == "daily":
            execute(cursor, """
                SELECT * FROM users
                WHERE account_status='Active'
                AND receive_daily_digest=1
            """)
        elif alert_type == "weekly":
            # Kept compatible with the existing project behaviour.
            execute(cursor, """
                SELECT * FROM users
                WHERE account_status='Active'
                AND receive_daily_digest=1
            """)
        elif alert_type == "critical":
            execute(cursor, """
                SELECT * FROM users
                WHERE account_status='Active'
                AND receive_critical_alerts=1
            """)
        else:
            return []
        return cursor.fetchall()
    finally:
        conn.close()


# ==========================================
# INITIAL DATABASE SETUP
# ==========================================
if __name__ == "__main__":
    create_table()
    if USE_POSTGRES:
        print("PostgreSQL database initialized successfully.")
    else:
        print("SQLite database initialized successfully.")
