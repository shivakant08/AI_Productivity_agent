import sqlite3

conn = sqlite3.connect("data/productivity.db")
cursor = conn.cursor()

print("--- TASKS TABLE ---")
cursor.execute("SELECT * FROM tasks")
for row in cursor.fetchall():
  print(row)

print("\n--- NOTES TABLE ---")
cursor.execute("SELECT * FROM notes")
for row in cursor.fetchall():
  print(row)

conn.close()