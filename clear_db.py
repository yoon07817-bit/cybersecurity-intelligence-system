import sqlite3

conn = sqlite3.connect("SAVE_DATA.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM articles")

conn.commit()
conn.close()

print("All articles deleted.")