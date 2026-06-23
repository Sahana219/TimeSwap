import sqlite3

conn = sqlite3.connect("timeswap.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE users
SET credits = 1000
""")

conn.commit()
conn.close()

print("Credits Updated Successfully!")