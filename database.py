import sqlite3

conn = sqlite3.connect("timeswap.db")
cursor = conn.cursor()

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    skills_offered TEXT,
    skills_needed TEXT,
    credits INTEGER DEFAULT 1000,
    reputation REAL DEFAULT 5.0
)
""")

# Questions / Tasks Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    question TEXT,
    reward INTEGER DEFAULT 10,
    attachment TEXT,
    date_posted TEXT
)
""")

# Answers Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS answers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    username TEXT,
    answer TEXT,
    attachment TEXT,
    date_posted TEXT,
    accepted INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")