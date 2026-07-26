import schedule
import time
import subprocess
import logging
import sys



# ==========================
# LOGGING
# ==========================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s"

)





# ==========================
# DAILY DIGEST
# ==========================

def run_digest():


    logging.info(
        "Starting daily digest..."
    )



    try:


        subprocess.run(

            [
                sys.executable,
                "main.py"
            ],

            check=True

        )



        logging.info(
            "Daily digest completed."
        )



    except Exception as e:


        logging.error(
            f"Digest failed: {e}"
        )







# ==========================
# HOURLY ALERT CHECK
# ==========================

def run_alert_check():


    logging.info(
        "Starting alert check..."
    )



    try:


        subprocess.run(

            [
                sys.executable,
                "alert_check.py"
            ],

            check=True

        )



        logging.info(
            "Alert check completed."
        )



    except Exception as e:


        logging.error(
            f"Alert check failed: {e}"
        )







# ==========================
# SCHEDULE
# ==========================


# Daily digest at 07:00 AM

schedule.every().day.at(
    "07:00"
).do(
    run_digest
)




# TEST MODE: Security monitoring every 2 minutes

schedule.every(2).minutes.do(
    run_alert_check
)





# ==========================
# START
# ==========================

logging.info(
    "Scheduler started."
)


logging.info(
    "Daily digest: 07:00 AM"
)


logging.info(
    "Alert monitoring: every hour"
)





# ==========================
# KEEP RUNNING
# ==========================

while True:


    schedule.run_pending()


    time.sleep(30)