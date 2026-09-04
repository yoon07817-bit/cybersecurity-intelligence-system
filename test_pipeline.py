import os
import sqlite3
import logging
from database import create_table, create_user, save_article, article_exists, DB_NAME
from alert import process_unhandled_critical_alerts
from main import main as run_main_pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")


def test_database_initialization():
    """Verify that the SQLite database and tables can be created."""
    print("\n--- TEST 1: Database Initialization ---")
    create_table()
    if os.path.exists(DB_NAME):
        print(f"SUCCESS: Database file '{DB_NAME}' exists.")
    else:
        print(f"FAILED: Database file '{DB_NAME}' was not created.")


def test_user_creation(test_email):
    """Verify creating a test subscriber in database."""
    print(f"\n--- TEST 2: User Creation ({test_email}) ---")
    try:
        user_id = create_user(test_email, "TestPassword123!")
        if user_id:
            print(f"SUCCESS: Created test user with ID: {user_id}")
        else:
            print(f"NOTICE: User '{test_email}' already exists in database.")
    except Exception as e:
        print(f"FAILED: User creation raised an exception: {e}")


def test_mock_critical_article_alert():
    """Inject a mock Critical vulnerability to verify the alert pipeline."""
    print("\n--- TEST 3: Mock Critical Article & Email Alerting ---")
    mock_url = "https://example.com/test-critical-zero-day-vulnerability"
    
    mock_article = {
        "title": "CRITICAL TEST: Zero-Day Remote Code Execution in Core Network Router",
        "url": mock_url,
        "source": "Security Test Feed",
        "category": "Vulnerability",
        "published_date": "2026-08-07",
        "content": "A test critical vulnerability allowing unauthorized remote code execution.",
        "summary": "Main Point: Critical zero-day RCE flaw discovered.\n- High risk of exploitation.\n- Urgent patching required.",
        "severity": "Critical",
        "score": 95,
        "critical_keywords": ["zero-day", "rce", "remote code execution"],
        "high_keywords": ["exploit"],
        "medium_keywords": []
    }

    if not article_exists(mock_url):
        save_article(mock_article)
        print("SUCCESS: Mock critical article inserted into database.")
    else:
        print("NOTICE: Mock article already exists in database.")

    # Trigger critical alert processing
    print("Triggering process_unhandled_critical_alerts()...")
    try:
        process_unhandled_critical_alerts()
        print("SUCCESS: Alert process executed without errors.")
    except Exception as e:
        print(f"FAILED: Alert process threw error: {e}")


def inspect_saved_articles():
    """Inspect stored records directly in SQLite."""
    print("\n--- TEST 4: SQLite Database Inspection ---")
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM articles")
        count = cursor.fetchone()[0]
        print(f"Total articles stored in 'articles' table: {count}")

        cursor.execute("SELECT title, source, severity, score FROM articles ORDER BY id DESC LIMIT 3")
        rows = cursor.fetchall()
        print("\nLatest 3 stored articles:")
        for r in rows:
            print(f" - [{r[2]} | Score: {r[3]}] {r[0]} ({r[1]})")
            
        conn.close()
    except Exception as e:
        print(f"FAILED: Database query error: {e}")


def run_full_live_pipeline():
    """Execute main.py live RSS scraping pipeline."""
    print("\n--- TEST 5: Live Pipeline Execution (main.py) ---")
    try:
        run_main_pipeline()
        print("SUCCESS: Live pipeline execution finished cleanly.")
    except Exception as e:
        print(f"FAILED: main.py execution error: {e}")


if __name__ == "__main__":
    print("==================================================")
    print("   AUTOMATED THREAT PIPELINE INTEGRATION TEST     ")
    print("==================================================")
    
    TEST_EMAIL = "your_email@example.com"  # <-- Replace with your testing email address
    
    # Run tests in order
    test_database_initialization()
    test_user_creation(TEST_EMAIL)
    test_mock_critical_article_alert()
    
    # Optionally run the live scraper pipeline
    run_live = input("\nDo you want to run the live RSS scraper (main.py)? (y/n): ")
    if run_live.lower().strip() == 'y':
        run_full_live_pipeline()

    inspect_saved_articles()
    
    print("\n==================================================")
    print("              ALL TESTS COMPLETED                ")
    print("==================================================")