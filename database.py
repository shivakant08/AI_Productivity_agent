# import sqlite3

# DB_PATH= "data/productivity.db"

# def init_db():
#     """ Initilaizes the SQLite database and creates the necessary tables."""
#     conn = sqlite3.connect(DB_PATH)
#     cursor= conn.cursor()

#     #Tasks table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS tasks(
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             title TEXT NOT NULL,
#             due_date TEXT
#             status TEXT DEFAULT 'PENDING' 
#             created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#             )   
#         """)

#     #Notes Table
#     cursor.execute(
#         """
#         CREATE TABLE IF NOT EXISTS notes (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         content TEXT NOT NULL,
#         created_at DATETIME DEFAULT CURRENT_TIMESTAMP
#         )
#     """)

#     conn.commit()
#     conn.close()

# if __name__ == "__main__":
#     init_db()
#     print("Database initialized successfully at data/productivity.db")

    

import os
import sqlite3

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "productivity.db")


def init_db():
  """Initializes the SQLite database, ensures directories exist,

  and creates necessary tables.
  """
  # Ensure the 'data' directory exists
  if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # Tasks table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

  # Notes table
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

  conn.commit()
  conn.close()


if __name__ == "__main__":
  init_db()
  print(f"Database initialized successfully at {DB_PATH}")