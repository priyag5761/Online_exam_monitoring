import pandas as pd
from datetime import datetime


# -----------------------------------
# Input / Output files
# -----------------------------------

EVENT_FILE = "event_logs.csv"
SESSION_FILE = "exam_sessions.csv"
PRESENCE_FILE = "face_presence.csv"
OUTPUT_FILE = "student_behavior.csv"


# -----------------------------------
# Event penalties
# -----------------------------------

PENALTIES = {
    "Face Absent": 10,
    "Multiple Faces": 20,
    "Tab Switched": 15
}


# -----------------------------------
# Read exam sessions
# -----------------------------------

try:
    sessions = pd.read_csv(SESSION_FILE)

    # Keep latest session for each student
    sessions["Start_dt"] = pd.to_datetime(
        sessions["Start"],
        errors="coerce"
    )

    sessions = (
        sessions
        .sort_values("Start_dt")
        .drop_duplicates("Username", keep="last")
    )

except FileNotFoundError:
    print("exam_sessions.csv not found.")
    sessions = pd.DataFrame(
        columns=["Username", "Start", "End"]
    )


# -----------------------------------
# Read event logs
# -----------------------------------

try:
    events = pd.read_csv(EVENT_FILE)

except FileNotFoundError:
    print("event_logs.csv not found.")
    events = pd.DataFrame(
        columns=["Timestamp", "Username", "Event", "Details"]
    )


# -----------------------------------
# Convert timestamps
# -----------------------------------

if not events.empty:
    events["Timestamp_dt"] = pd.to_datetime(
        events["Timestamp"],
        errors="coerce"
    )


# -----------------------------------
# Calculate event counts
# -----------------------------------

students = []

for _, session in sessions.iterrows():

    username = session["Username"]

    session_start = pd.to_datetime(
        session["Start"],
        errors="coerce"
    )

    if pd.notna(session["End"]) and str(session["End"]).strip():
        session_end = pd.to_datetime(
            session["End"],
            errors="coerce"
        )
    else:
        session_end = pd.Timestamp.now()

    # Events belonging to this student's latest exam
    student_events = events[
        (events["Username"] == username) &
        (events["Timestamp_dt"] >= session_start) &
        (events["Timestamp_dt"] <= session_end)
    ]

    face_absent = (
        student_events["Event"]
        .eq("Face Absent")
        .sum()
    )

    multiple_faces = (
        student_events["Event"]
        .eq("Multiple Faces")
        .sum()
    )

    tab_switches = (
        student_events["Event"]
        .eq("Tab Switched")
        .sum()
    )

    # Total suspicious events
    total_events = (
        face_absent
        + multiple_faces
        + tab_switches
    )


    # -----------------------------------
    # Weighted event score
    # -----------------------------------

    event_penalty = (
        face_absent * PENALTIES["Face Absent"]
        + multiple_faces * PENALTIES["Multiple Faces"]
        + tab_switches * PENALTIES["Tab Switched"]
    )

    event_score = max(0, 100 - event_penalty)


    # -----------------------------------
    # Face presence ratio
    # -----------------------------------

    presence_ratio = None

    try:

        presence = pd.read_csv(PRESENCE_FILE)

        student_presence = presence[
            presence["Username"] == username
        ]

        if not student_presence.empty:
            presence_ratio = float(
                student_presence.iloc[-1]["Presence_Ratio"]
            )

    except FileNotFoundError:
        print("face_presence.csv not found.")


    # -----------------------------------
    # Calculate integrity score
    # -----------------------------------

    if presence_ratio is not None:

        presence_score = presence_ratio * 100

        # 70% face presence + 30% event behaviour
        integrity_score = (
            0.70 * presence_score
            + 0.30 * event_score
        )

    else:

        # If presence data is unavailable,
        # use event score only.
        integrity_score = event_score


    integrity_score = round(
        max(0, min(100, integrity_score)),
        2
    )


    students.append({
        "Username": username,
        "Face_Absent": face_absent,
        "Multiple_Faces": multiple_faces,
        "Tab_Switches": tab_switches,
        "Total_Suspicious_Events": total_events,
        "Face_Presence_Ratio": (
            round(presence_ratio, 4)
            if presence_ratio is not None
            else "Not Available"
        ),
        "Integrity_Score": integrity_score
    })


# -----------------------------------
# Create DataFrame
# -----------------------------------

behavior_df = pd.DataFrame(students)


# -----------------------------------
# Save dataset
# -----------------------------------

behavior_df.to_csv(
    OUTPUT_FILE,
    index=False
)


print("\nCurrent exam session behavior dataset created successfully!\n")

print(behavior_df)