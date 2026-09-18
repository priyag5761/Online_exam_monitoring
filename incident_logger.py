import sqlite3
from datetime import datetime


DATABASE = "examguard.db"


def create_incident_table():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            event_type TEXT NOT NULL,

            details TEXT,

            timestamp TEXT NOT NULL,

            severity TEXT NOT NULL,

            screenshot_path TEXT

        )
    """)

    conn.commit()

    conn.close()


def log_incident(
    username,
    event_type,
    details,
    severity="Medium",
    screenshot_path=None
):

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO incidents
        (
            username,
            event_type,
            details,
            timestamp,
            severity,
            screenshot_path
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        username,
        event_type,
        details,
        timestamp,
        severity,
        screenshot_path
    ))

    conn.commit()

    conn.close()
    
    
if __name__ == "__main__":

    create_incident_table()

    print(
        "Incident table created successfully!"
    )