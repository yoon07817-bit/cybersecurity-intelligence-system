import sqlite3

DB_NAME = "save_data.db"


conn = sqlite3.connect(DB_NAME)

cursor = conn.cursor()


try:

    cursor.execute("""
        ALTER TABLE articles
        ADD COLUMN alert_sent INTEGER DEFAULT 0
    """)

    conn.commit()

    print("Database updated successfully!")

except Exception as e:

    print(e)


conn.close()