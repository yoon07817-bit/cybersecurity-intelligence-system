import sqlite3

conn = sqlite3.connect("save_data.db")
cursor = conn.cursor()

# Count rows
cursor.execute("SELECT COUNT(*) FROM articles")
count = cursor.fetchone()[0]

print("Number of articles:", count)

# Show all saved articles
cursor.execute("""
SELECT title, source, published_date
FROM articles
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()