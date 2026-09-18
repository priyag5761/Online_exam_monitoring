from faker import Faker
import csv
import random

fake = Faker()

with open("session_logs.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Session ID",
        "Candidate Name",
        "Login Time",
        "Camera Status",
        "Integrity Score"
    ])

    for i in range(1, 11):

        writer.writerow([
            1000 + i,
            fake.name(),
            fake.time(),
            random.choice(["Active", "Inactive", "Warning"]),
            random.randint(80, 100)
        ])

print("Session logs generated successfully!")