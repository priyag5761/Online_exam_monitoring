import csv
import os                  #checks if log file exists
from datetime import datetime    #timestamp


LOG_FILE = "event_logs.csv"


def log_event(event, details, username):

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Timestamp",
                "Username",
                "Event",
                "Details"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            username,
            event,
            details
        ])