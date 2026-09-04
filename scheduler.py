import logging
import os
import subprocess
import sys
import time

import schedule


# ==========================================
# IMPORT WORKFLOW FUNCTIONS
# ==========================================

try:

    import main

    from alert import (
        process_unhandled_critical_alerts
    )

    from database import (
        get_articles_today
    )

    from emailer import (
        send_email
    )

    DIRECT_IMPORT_AVAILABLE = True


except ImportError:

    DIRECT_IMPORT_AVAILABLE = False





# ==========================================
# LOGGING CONFIGURATION
# ==========================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - [%(levelname)s] - %(message)s",

    handlers=[
        logging.StreamHandler(sys.stdout)
    ]

)





# ==========================================
# FEED INGESTION
# ==========================================

def run_ingestion():

    logging.info(
        "Starting Feed Ingestion..."
    )


    try:


        if DIRECT_IMPORT_AVAILABLE and hasattr(
            main,
            "run_pipeline"
        ):


            main.run_pipeline()


            logging.info(
                "Feed Ingestion completed."
            )



        else:


            script_path = os.path.join(

                os.path.dirname(__file__),

                "main.py"

            )


            subprocess.run(

                [
                    sys.executable,
                    script_path
                ],

                check=True

            )


            logging.info(
                "Feed Ingestion completed via main.py."
            )



    except Exception as e:


        logging.error(

            f"Feed Ingestion failed: {e}",

            exc_info=True

        )







# ==========================================
# DAILY DIGEST EMAIL
# ==========================================

def run_digest():


    logging.info(
        "Starting Daily Digest..."
    )


    try:


        if DIRECT_IMPORT_AVAILABLE:


            articles = [

                dict(row)

                for row in get_articles_today()

            ]



            if articles:


                send_email(

                    articles,

                    alert_type="daily"

                )


                logging.info(

                    f"Daily Digest sent: {len(articles)} articles"

                )



            else:


                logging.info(

                    "No articles available."

                )



        else:


            logging.warning(

                "Direct import unavailable."

            )



    except Exception as e:


        logging.error(

            f"Daily Digest failed: {e}",

            exc_info=True

        )







# ==========================================
# CRITICAL ALERT CHECK
# ==========================================

def run_alert_check():


    logging.info(

        "Starting Critical Alert Check..."

    )


    try:


        if DIRECT_IMPORT_AVAILABLE:


            process_unhandled_critical_alerts()


            logging.info(

                "Critical Alert Check completed."

            )



        else:


            script_path = os.path.join(

                os.path.dirname(__file__),

                "alert_check.py"

            )


            subprocess.run(

                [
                    sys.executable,
                    script_path
                ],

                check=True

            )


            logging.info(

                "Alert check completed."

            )



    except Exception as e:


        logging.error(

            f"Critical Alert failed: {e}",

            exc_info=True

        )







# ==========================================
# DEMO SCHEDULE CONFIGURATION
# ==========================================

# For supervisor demonstration only

# Feed collection every 2 minute

schedule.every(2).minutes.do(
    run_ingestion
)



# Critical alert checking every 2 minute

schedule.every(2).minutes.do(
    run_alert_check
)



# Daily digest every 10 minutes for demo

schedule.every(10).minutes.do(
    run_digest
)







# ==========================================
# START SCHEDULER
# ==========================================

if __name__ == "__main__":


    logging.info(
        "=========================================="
    )

    logging.info(
        " Security Digest Scheduler DEMO Mode"
    )

    logging.info(
        "=========================================="
    )


    logging.info(
        "Feed Ingestion : Every 2 minutes"
    )


    logging.info(
        "Critical Alert : Every 2 minutes"
    )


    logging.info(
        "Daily Digest   : Every 10 minutes"
    )


    logging.info(
        "Press CTRL+C to stop."
    )




    # Run immediately when started

    run_ingestion()

    run_alert_check()



    try:


        while True:


            schedule.run_pending()


            time.sleep(10)



    except KeyboardInterrupt:


        logging.info(
            "Scheduler stopped."
        )