import json
import os
import sys
import markdown

from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.append(BASE_DIR)

import database


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)

app.secret_key = os.getenv(
    "FLASK_SECRET_KEY",
    "security_digest_secret_key_change_in_production"
)


# =========================================================
# DATABASE HELPERS
# =========================================================

def _row_to_dict(row, cursor=None):
    """Convert a PostgreSQL result row to a normal dictionary."""
    if row is None:
        return None

    if isinstance(row, dict):
        return dict(row)

    try:
        return dict(row)
    except (TypeError, ValueError):
        if cursor is not None and cursor.description:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))

    return row


def db_fetch_all(query, params=()):
    """Run a SELECT query using the PostgreSQL connection from database.py."""
    conn = database.create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_row_to_dict(row, cursor) for row in rows]
    finally:
        cursor.close()
        conn.close()


def db_fetch_one(query, params=()):
    """Run a SELECT query and return one PostgreSQL row as a dictionary."""
    conn = database.create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        row = cursor.fetchone()
        return _row_to_dict(row, cursor)
    finally:
        cursor.close()
        conn.close()


def db_execute(query, params=()):
    """Run an INSERT/UPDATE/DELETE query through database.py."""
    conn = database.create_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(query, params)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# =========================================================
# FLASK LOGIN CONFIGURATION
# =========================================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = (
    "Please log in to access this page."
)

login_manager.login_message_category = "warning"


# =========================================================
# USER CLASS
# =========================================================

class User(UserMixin):

    def __init__(self, user_dict):

        self.id = user_dict["id"]

        self.email = user_dict["email"]

        self.receive_daily_digest = (
            user_dict["receive_daily_digest"]
        )

        self.receive_critical_alerts = (
            user_dict["receive_critical_alerts"]
        )

        self.account_status = (
            user_dict["account_status"]
        )

        self.last_login = (
            user_dict["last_login"]
        )

        self.login_count = (
            user_dict["login_count"]
        )

        self.role = (
            user_dict["role"]
        )


# =========================================================
# USER LOADER
# =========================================================

@login_manager.user_loader
def load_user(user_id):

    user_data = database.get_user_by_id(
        user_id
    )

    if user_data:

        user_dict = dict(
            user_data
        )

        if user_dict["account_status"] == "Disabled":

            return None

        return User(
            user_dict
        )

    return None


# =========================================================
# ADMIN PERMISSION CHECK
# =========================================================

def admin_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not current_user.is_authenticated:

            return redirect(
                url_for("login")
            )

        if current_user.role != "Admin":

            return "Access denied", 403

        return func(
            *args,
            **kwargs
        )

    return wrapper


# =========================================================
# CACHE CONTROL
# =========================================================

@app.after_request
def add_header(response):

    response.headers["Cache-Control"] = (
        "no-cache, no-store, must-revalidate"
    )

    response.headers["Pragma"] = "no-cache"

    response.headers["Expires"] = "0"

    return response


# =========================================================
# HOME DASHBOARD
# =========================================================

@app.route("/")
@login_required
def home():

    keyword = request.args.get(
        "search",
        ""
    ).strip()

    selected_severity = request.args.get(
        "severity",
        ""
    ).strip()

    selected_category = request.args.get(
        "category",
        ""
    ).strip()

    categories = db_fetch_all(
        """
        SELECT DISTINCT category
        FROM articles
        WHERE category IS NOT NULL
        AND category != ''
        ORDER BY category
        """
    )

    severities = [
        "Critical",
        "High",
        "Medium",
        "Low"
    ]

    where_clauses = []
    params = []

    if keyword:
        where_clauses.append(
            """
            (
                title ILIKE %s
                OR summary ILIKE %s
                OR category ILIKE %s
                OR source ILIKE %s
            )
            """
        )

        params.extend(
            [
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%",
                f"%{keyword}%"
            ]
        )

    if selected_severity:
        where_clauses.append(
            "severity = %s"
        )
        params.append(
            selected_severity
        )

    if selected_category:
        where_clauses.append(
            "category = %s"
        )
        params.append(
            selected_category
        )

    where_str = ""

    if where_clauses:
        where_str = (
            " WHERE "
            + " AND ".join(where_clauses)
        )

    articles = db_fetch_all(
        f"""
        SELECT *
        FROM articles
        {where_str}
        ORDER BY published_date DESC NULLS LAST, id DESC
        """,
        tuple(params)
    )

    return render_template(
        "index.html",
        articles=articles,
        categories=categories,
        severities=severities,
        selected_severity=selected_severity,
        selected_category=selected_category,
        keyword=keyword,
        total_articles=len(articles),
        page=1,
        total_pages=1
    )


# =========================================================
# ARTICLE PAGE
# =========================================================

@app.route("/article/<int:id>")
@login_required
def article(id):

    article_data = db_fetch_one(
        """
        SELECT *
        FROM articles
        WHERE id = %s
        """,
        (id,)
    )

    if not article_data:
        return "Article not found", 404

    article_dict = dict(article_data)

    if article_dict.get("summary"):
        article_dict["summary"] = markdown.markdown(
            article_dict["summary"]
        )

    cve_list = []

    try:
        cve_rows = database.get_cve_by_article(id)

        if cve_rows:
            for row in cve_rows:
                cve_list.append(
                    _row_to_dict(row)
                )

    except Exception as e:
        print(
            f"CVE lookup failed: {e}"
        )
        cve_list = []

    if not cve_list:
        import re

        summary_text = (
            article_data.get("summary") or ""
        )

        found_cves = re.findall(
            r"\bCVE-\d{4}-\d{4,}\b",
            summary_text,
            re.IGNORECASE
        )

        seen = set()

        for cve in found_cves:
            cve = cve.upper()

            if cve not in seen:
                seen.add(cve)

                cve_list.append(
                    {
                        "cve_id": cve,
                        "cvss_score": None,
                        "severity": article_dict.get(
                            "severity",
                            "Unknown"
                        ),
                        "description": "",
                        "affected_product": ""
                    }
                )

    recommendation = None

    try:
        recommendation = database.get_recommendation(
            article_dict.get(
                "category",
                "General Security"
            ),
            article_dict.get(
                "severity",
                "Low"
            )
        )

    except Exception as e:
        print(
            f"Recommendation lookup failed: {e}"
        )

    if not recommendation:
        recommendation = (
            "Review the affected systems, apply "
            "available security updates, monitor "
            "for suspicious activity, and follow "
            "appropriate cybersecurity best practices."
        )

    return render_template(
        "article.html",
        article=article_dict,
        cves=cve_list,
        recommendation=recommendation
    )


# =========================================================
# STATISTICS
# =========================================================

@app.route("/stats")
@login_required
def stats():

    total_row = db_fetch_one(
        "SELECT COUNT(*) AS count FROM articles"
    )

    total = (
        total_row["count"]
        if total_row
        else 0
    )

    severity_rows = db_fetch_all(
        """
        SELECT severity,
               COUNT(*) AS count
        FROM articles
        GROUP BY severity
        ORDER BY count DESC
        """
    )

    category_rows = db_fetch_all(
        """
        SELECT category,
               COUNT(*) AS count
        FROM articles
        GROUP BY category
        ORDER BY count DESC
        """
    )

    sources = db_fetch_all(
        """
        SELECT source,
               COUNT(*) AS count
        FROM articles
        GROUP BY source
        ORDER BY count DESC
        """
    )

    severity_dict = {
        "Critical": 0,
        "High": 0,
        "Medium": 0,
        "Low": 0
    }

    for row in severity_rows:
        severity = row.get("severity")

        if severity in severity_dict:
            severity_dict[
                severity
            ] = row.get("count", 0)

    category_labels = [
        row.get("category") or "Uncategorized"
        for row in category_rows
    ]

    category_counts = [
        row.get("count", 0)
        for row in category_rows
    ]

    return render_template(
        "stats.html",
        total=total,
        severity_items=severity_rows,
        category_items=category_rows,
        sources=sources,
        severity_json=json.dumps(
            severity_dict,
            default=str
        ),
        category_labels_json=json.dumps(
            category_labels,
            default=str
        ),
        category_counts_json=json.dumps(
            category_counts,
            default=str
        ),
        daily_labels_json=json.dumps([]),
        daily_counts_json=json.dumps([])
    )


# =========================================================
# REGISTER
# =========================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    print(
        ">>> REGISTER ROUTE CALLED <<<"
    )

    if request.method == "POST":

        print(
            ">>> REGISTER POST RECEIVED <<<"
        )

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        print(
            ">>> REGISTER EMAIL:",
            email
        )

        print(
            ">>> PASSWORD RECEIVED:",
            bool(password)
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return render_template(
                "register.html"
            )

        if database.create_user(
            email,
            password
        ):

            print(
                ">>> REGISTRATION SUCCESS <<<"
            )

            flash(
                "Registration successful.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        print(
            ">>> REGISTRATION FAILED - EMAIL EXISTS <<<"
        )

        flash(
            "Email already exists.",
            "warning"
        )

    return render_template(
        "register.html"
    )


# =========================================================
# SIMPLE PHONE TEST
# =========================================================

@app.route("/post-test")
def post_test():

    print(
        ">>> POST TEST PAGE <<<"
    )

    return "HELLO FROM FLASK - PHONE TEST"


# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    print(
        ">>> LOGIN ROUTE CALLED <<<"
    )

    if request.method == "POST":

        print(
            ">>> LOGIN POST RECEIVED <<<"
        )

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        print(
            ">>> EMAIL:",
            email
        )

        print(
            ">>> PASSWORD RECEIVED:",
            bool(password)
        )

        user_data = database.verify_user(
            email,
            password
        )

        if user_data:

            print(
                ">>> LOGIN SUCCESS <<<"
            )

            database.update_last_login(
                user_data["id"]
            )

            updated_user = database.get_user_by_id(
                user_data["id"]
            )

            login_user(
                User(
                    dict(updated_user)
                )
            )

            print(
                ">>> USER SESSION CREATED <<<"
            )

            flash(
                "Login successful.",
                "success"
            )

            next_page = request.args.get(
                "next"
            )

            if next_page:

                return redirect(
                    next_page
                )

            return redirect(
                url_for("home")
            )

        print(
            ">>> LOGIN FAILED <<<"
        )

        flash(
            "Invalid login or disabled account.",
            "danger"
        )

        return render_template(
            "login.html"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# SETTINGS
# =========================================================

@app.route(
    "/settings",
    methods=["GET", "POST"]
)
@login_required
def settings():

    if request.method == "POST":

        daily = 1 if request.form.get(
            "receive_daily_digest"
        ) else 0

        critical = 1 if request.form.get(
            "receive_critical_alerts"
        ) else 0

        severity = request.form.get(
            "minimum_severity",
            "Low"
        )

        database.update_user_preferences(

            current_user.id,

            daily,

            critical,

            severity

        )

        flash(
            "Preferences updated successfully.",
            "success"
        )

        return redirect(
            url_for("settings")
        )

    user = database.get_user_by_id(
        current_user.id
    )

    return render_template(
        "settings.html",
        user=dict(user)
    )


# =========================================================
# ADMIN USERS
# =========================================================

@app.route("/users")
@login_required
@admin_required
def users():

    users = database.get_all_users()

    return render_template(
        "users.html",
        users=users
    )


# =========================================================
# CREATE USER
# =========================================================

@app.route(
    "/create-user",
    methods=["GET", "POST"]
)
@login_required
@admin_required
def create_user():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "User"
        )

        if not email or not password:

            flash(
                "Email and password are required.",
                "danger"
            )

            return redirect(
                url_for("create_user")
            )

        success = database.create_user(
            email,
            password
        )

        if success:

            # database.py handles the PostgreSQL connection.
            # create_user() uses the default User role, so the
            # selected administrator role is updated here.
            db_execute(
                """
                UPDATE users
                SET role = %s
                WHERE email = %s
                """,
                (
                    role,
                    email
                )
            )

            flash(
                "User created successfully.",
                "success"
            )

            return redirect(
                url_for("users")
            )

        flash(
            "Email already exists.",
            "warning"
        )

    return render_template(
        "create_user.html"
    )


# =========================================================
# DISABLE USER
# =========================================================

@app.route(
    "/disable-user/<int:user_id>"
)
@login_required
@admin_required
def disable_user(user_id):

    database.disable_user(
        user_id
    )

    flash(
        "User account disabled.",
        "warning"
    )

    return redirect(
        url_for("users")
    )


# =========================================================
# ENABLE USER
# =========================================================

@app.route(
    "/enable-user/<int:user_id>"
)
@login_required
@admin_required
def enable_user(user_id):

    database.enable_user(
        user_id
    )

    flash(
        "User account enabled.",
        "success"
    )

    return redirect(
        url_for("users")
    )


# =========================================================
# DELETE USER
# =========================================================

@app.route(
    "/delete-user/<int:user_id>"
)
@login_required
@admin_required
def delete_user(user_id):

    database.delete_user(
        user_id
    )

    flash(
        "User deleted successfully.",
        "danger"
    )

    return redirect(
        url_for("users")
    )


# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():

    return render_template(
        "about.html"
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    database.create_table()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )