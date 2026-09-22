import logging
import os
import subprocess
import sys
import time

import schedule


# ==========================================================
# CONFIGURATION
# ==========================================================

from config import (
    TEST_MODE,
    DATA_COLLECTION_INTERVAL,
    CRITICAL_ALERT_INTERVAL,
    DAILY_DIGEST_HOUR
)


# ==========================================================
# DATABASE / EMAIL IMPORTS
# ==========================================================

try:

    from database import (
        get_articles_today
    )

    from emailer import (
        send_email
    )

    DATABASE_EMAIL_AVAILABLE = True


except ImportError as e:

    DATABASE_EMAIL_AVAILABLE = False

    logging.warning(
        f"Database/email import unavailable: {e}"
    )


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s - "
        "[%(levelname)s] - "
        "%(message)s"
    ),

    handlers=[
        logging.StreamHandler(sys.stdout)
    ]

)


# ==========================================================
# PROJECT DIRECTORY
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ==========================================================
# RUN PYTHON SCRIPT
# ==========================================================

def run_script(
    script_name
):

    script_path = os.path.join(
        BASE_DIR,
        script_name
    )


    if not os.path.exists(
        script_path
    ):

        logging.error(
            f"Script not found: {script_path}"
        )

        return False


    try:

        subprocess.run(

            [
                sys.executable,
                script_path
            ],

            check=True

        )

        return True


    except subprocess.CalledProcessError as e:

        logging.error(

            f"{script_name} failed "
            f"with exit code {e.returncode}."

        )

        return False


    except Exception as e:

        logging.error(

            f"Failed to run {script_name}: {e}",

            exc_info=True

        )

        return False


# ==========================================================
# DATA COLLECTION
# ==========================================================

def run_ingestion():

    logging.info(
        "Starting Feed Ingestion..."
    )


    success = run_script(
        "main.py"
    )


    if success:

        logging.info(
            "Feed Ingestion completed."
        )

    else:

        logging.error(
            "Feed Ingestion failed."
        )


# ==========================================================
# CRITICAL ALERT CHECK
# ==========================================================

def run_alert_check():

    logging.info(
        "Starting Critical Alert Check..."
    )


    # IMPORTANT:
    #
    # alert_check.py is responsible for:
    #
    # 1. Fetching RSS articles
    # 2. Applying 24-hour filtering
    # 3. Checking Critical severity
    # 4. Saving new Critical articles
    # 5. Sending Critical emails
    # 6. Marking alerts as sent
    #
    # scheduler.py only starts the process.


    success = run_script(
        "alert_check.py"
    )


    if success:

        logging.info(
            "Critical Alert Check completed."
        )

    else:

        logging.error(
            "Critical Alert Check failed."
        )


# ==========================================================
# DAILY DIGEST
# ==========================================================

def run_digest():

    logging.info(
        "Starting Daily Digest..."
    )


    if not DATABASE_EMAIL_AVAILABLE:

        logging.error(
            "Database/email modules are unavailable."
        )

        return


    try:

        # ==================================================
        # GET TODAY'S ARTICLES
        # ==================================================

        rows = get_articles_today()


        articles = [

            dict(row)

            for row in rows

        ]


        logging.info(
            f"Articles available for digest: "
            f"{len(articles)}"
        )


        # ==================================================
        # NO ARTICLES
        # ==================================================

        if not articles:

            logging.info(
                "No articles available for Daily Digest."
            )

            return


        # ==================================================
        # SEND DAILY DIGEST
        # ==================================================

        success = send_email(

            articles,

            alert_type="daily"

        )


        if success:

            logging.info(

                "Daily Digest sent successfully: "
                f"{len(articles)} articles"

            )

        else:

            logging.warning(
                "Daily Digest was not sent."
            )


    except Exception as e:

        logging.error(

            f"Daily Digest failed: {e}",

            exc_info=True

        )


# ==========================================================
# CLEAR PREVIOUS SCHEDULES
# ==========================================================

schedule.clear()


# ==========================================================
# TEST MODE
# ==========================================================

if TEST_MODE:

    logging.info(
        "Scheduler configured for TEST MODE."
    )


    # ------------------------------------------------------
    # DATA COLLECTION
    # Every 1 minute
    # ------------------------------------------------------

    schedule.every(
        DATA_COLLECTION_INTERVAL
    ).seconds.do(
        run_ingestion
    )


    # ------------------------------------------------------
    # CRITICAL ALERT
    # Every 2 minutes
    # ------------------------------------------------------

    schedule.every(
        CRITICAL_ALERT_INTERVAL
    ).seconds.do(
        run_alert_check
    )


    # ------------------------------------------------------
    # DAILY DIGEST
    #
    # Every 3 minutes for supervisor demonstration.
    #
    # This is ONLY temporary testing.
    # ------------------------------------------------------

    schedule.every(
        180
    ).seconds.do(
        run_digest
    )


# ==========================================================
# PRODUCTION MODE
# ==========================================================

else:

    logging.info(
        "Scheduler configured for PRODUCTION MODE."
    )


    # ------------------------------------------------------
    # DATA COLLECTION
    # Every 10 minutes
    # ------------------------------------------------------

    schedule.every(
        DATA_COLLECTION_INTERVAL
    ).seconds.do(
        run_ingestion
    )


    # ------------------------------------------------------
    # CRITICAL ALERT
    # Every 1 hour
    # ------------------------------------------------------

    schedule.every(
        CRITICAL_ALERT_INTERVAL
    ).seconds.do(
        run_alert_check
    )


    # ------------------------------------------------------
    # DAILY DIGEST
    # Every day at 7:00 AM
    # ------------------------------------------------------

    if DAILY_DIGEST_HOUR is not None:

        schedule.every().day.at(

            f"{DAILY_DIGEST_HOUR:02d}:00"

        ).do(
            run_digest
        )


# ==========================================================
# DISPLAY CONFIGURATION
# ==========================================================

def display_configuration():

    print()
    print(
        "=" * 60
    )


    if TEST_MODE:

        print(
            " SECURITY DIGEST SCHEDULER - TEST MODE"
        )

    else:

        print(
            " SECURITY DIGEST SCHEDULER - PRODUCTION MODE"
        )


    print(
        "=" * 60
    )


    if TEST_MODE:

        print(
            "Data Collection : "
            f"Every {DATA_COLLECTION_INTERVAL} seconds"
        )


        print(
            "Critical Alert  : "
            f"Every {CRITICAL_ALERT_INTERVAL} seconds"
        )


        print(
            "Daily Digest    : "
            "Every 3 minutes"
        )


    else:

        print(
            "Data Collection : "
            "Every 10 minutes"
        )


        print(
            "Critical Alert  : "
            "Every 1 hour"
        )


        print(
            "Daily Digest    : "
            "Every day at 07:00"
        )


    print(
        "=" * 60
    )


    print(
        "Press CTRL+C to stop."
    )


    print(
        "=" * 60
    )


# ==========================================================
# MAIN SCHEDULER
# ==========================================================

if __name__ == "__main__":

    display_configuration()


    # ======================================================
    # INITIAL DATA COLLECTION
    # ======================================================

    logging.info(
        "Running initial data collection..."
    )


    run_ingestion()


    # ======================================================
    # INITIAL CRITICAL CHECK
    # ======================================================

    logging.info(
        "Running initial Critical Alert Check..."
    )


    run_alert_check()


    # ======================================================
    # DO NOT RUN DAILY DIGEST IMMEDIATELY
    # ======================================================
    #
    # The Daily Digest waits for its scheduled time.
    #
    # In TEST MODE:
    #       every 3 minutes
    #
    # In PRODUCTION:
    #       07:00 AM
    #
    # This prevents an unnecessary duplicate digest
    # when scheduler.py starts.
    #


    # ======================================================
    # SCHEDULER LOOP
    # ======================================================

    try:

        while True:

            schedule.run_pending()

            time.sleep(5)


    except KeyboardInterrupt:

        logging.info(
            "Scheduler stopped by user."
        )

        schedule.clear()