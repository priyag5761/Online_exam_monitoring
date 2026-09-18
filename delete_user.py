import sqlite3

conn = sqlite3.connect("examguard.db")
cursor = conn.cursor()

# cursor.execute("DELETE FROM users WHERE username = ?", ("P",))
cursor.execute("DELETE FROM users")

conn.commit()
conn.close()

print("User deleted successfully!")