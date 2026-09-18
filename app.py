from flask import Flask , render_template , Response, request , session , redirect, url_for
from monitoring import generate_monitoring_frames , get_current_status 
from capture_photo import capture_photo
from datetime import datetime
from ai_agent import generate_ai_report
from flask import send_from_directory
import sqlite3
import subprocess
import sys
import csv
import os
import cv2


import base64
import os
import uuid

from rule_engine import get_score , deduct_marks, reset_score

app = Flask(__name__)

app.secret_key = "examguard_secret_key"

@app.route("/")
def home():
     return render_template("index.html")



@app.route("/exam")
def exam():

    if "username" not in session:
        return redirect(url_for("login"))

    # Start a new exam session
    reset_score()

    session["exam_session_start"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Save exam session
    session_file = "exam_sessions.csv"

    file_exists = os.path.isfile(session_file)

    with open(session_file, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Username",
                "Start",
                "End"
            ])

        writer.writerow([
            session["username"],
            session["exam_session_start"],
            ""
        ])

    return render_template("exam.html")






@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # return f"Welcome {username}"
        conn = sqlite3.connect("examguard.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = cursor.fetchone()

        conn.close()

        # if user:
        #     # return f"Welcome {username}!"
        #     session["username"] = username
        #     # return "Login Successful!"
        #     return redirect(url_for("dashboard"))
        
        if user:

            # Start with a fresh integrity score
            reset_score()

            # Clear any previous exam session
            session.pop("exam_session_start", None)

            session["username"] = username

            return redirect(url_for("dashboard"))
        else:
            return "Invalid Username or Password"


    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
    
        username = request.form["username"]
        password = request.form["password"]

        photo_taken = capture_photo(username)

        if not photo_taken:
            return "Photo capture cancelled."

        conn = sqlite3.connect("examguard.db")
        cursor = conn.cursor()

        cursor.execute(
        "INSERT INTO users(username,password) VALUES(?,?)",
        (username,password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))
    return render_template("register.html")



# @app.route("/dashboard")
# def dashboard():

#     if "username" not in session:
#         return redirect(url_for("login"))

#     logs = []
#     integrity_score = 100

#     try:
#         with open("session_logs.csv", "r") as file:

#             reader = csv.DictReader(file)

#             for row in reader:
#                 logs.append(row)

#         logs = logs[-5:]

#         if logs:
#             integrity_score = logs[-1]["Integrity Score"]

#     except FileNotFoundError:
#         logs = []

#     return render_template(
#         "dashboard.html",
#         username=session["username"],
#         logs=logs,
#         integrity_score=integrity_score
#     )



# @app.route("/dashboard")
# def dashboard():

#     if "username" not in session:
#         return redirect(url_for("login"))

#     integrity_score = get_score()

#     return render_template(
#         "dashboard.html",
#         username=session["username"],
#         integrity_score=integrity_score
#     )


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"]
    )


# @app.route("/camera")
# def camera():

#     print("Camera button clicked")

#     if "username" not in session:
#         return redirect(url_for("login"))

#     try:
#         # subprocess.Popen([sys.executable, "camera.py"])
#         # subprocess.Popen([sys.executable, "face_detection.py"])
#         subprocess.Popen([
#         sys.executable,
#         "face_detection.py",
#         session["username"]
#         ])
#         print("Camera started")
#     except Exception as e:
#         print(e)

#     return redirect(url_for("dashboard"))




# @app.route("/camera")
# def camera():

#     if "username" not in session:
#         return redirect(url_for("login"))

#     # Start a fresh exam
#     reset_score()

#     # Create a new exam session
#     session["exam_session_start"] = (
#         datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     )

#     return redirect(url_for("exam"))







@app.route("/camera")
def camera():

    if "username" not in session:
        return redirect(url_for("login"))

    # Start a fresh exam
    reset_score()

    # Create a new exam session
    session["exam_session_start"] = (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    # Save exam session
    session_file = "exam_sessions.csv"

    file_exists = os.path.isfile(session_file)

    with open(session_file, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Username",
                "Start",
                "End"
            ])

        writer.writerow([
            session["username"],
            session["exam_session_start"],
            ""
        ])

    return redirect(url_for("exam"))








# @app.route("/log_browser_event", methods=["POST"])
# def log_browser_event():

#     from event_logger import log_event
#     from rule_engine import deduct_marks
#     from incident_logger import log_incident

#     if "username" not in session:
#         return "Unauthorized", 401

#     event = request.form["event"]

#     log_event(
#         event,
#         "Browser Activity",
#         session["username"]
#     )

#     # Deduct marks only when student leaves the exam
#     if event == "Tab Switched":

#         log_incident(
#             session["username"],
#             "Tab Switched",
#             "Browser tab switched during exam",
#             "Medium"
#         )

#         deduct_marks(event)
        
#     return "OK"






@app.route("/log_browser_event", methods=["POST"])
def log_browser_event():

    from event_logger import log_event
    from rule_engine import deduct_marks
    from incident_logger import log_incident

    if "username" not in session:
        return "Unauthorized", 401

    event = request.form.get("event")

    username = session["username"]

    # -----------------------------------
    # Log normal browser event
    # -----------------------------------

    log_event(
        event,
        "Browser Activity",
        username
    )

    # -----------------------------------
    # Handle tab switch evidence
    # -----------------------------------

    if event == "Tab Switched":

        screenshot_path = None

        screenshot_data = request.form.get(
            "screenshot"
        )

        if screenshot_data:
            
            print("Screenshot received from browser!")

            try:

                # Remove "data:image/png;base64,"
                # from the beginning
                if "," in screenshot_data:
                    screenshot_data = screenshot_data.split(
                        ",", 1
                    )[1]

                image_data = base64.b64decode(
                    screenshot_data
                )

                # Create evidence folder
                evidence_folder = "evidence"

                os.makedirs(
                    evidence_folder,
                    exist_ok=True
                )

                # Generate safe unique filename
                filename = (
                    f"{username}_"
                    f"{uuid.uuid4().hex}.png"
                )

                screenshot_path = os.path.join(
                    evidence_folder,
                    filename
                )

                # Save screenshot
                with open(
                    screenshot_path,
                    "wb"
                ) as image_file:

                    image_file.write(
                        image_data
                    )

            except Exception as e:

                print(
                    "Screenshot save error:",
                    e
                )

                screenshot_path = None

        # -----------------------------------
        # Store incident in SQLite
        # -----------------------------------

        log_incident(
            username,
            "Tab Switched",
            "Browser tab switched during exam",
            "Medium",
            screenshot_path
        )

        # -----------------------------------
        # Deduct marks
        # -----------------------------------

        deduct_marks(event)

    return "OK"








# @app.route("/invigilator")
# def invigilator():

#     if "username" not in session:
#         return redirect(url_for("login"))
    
#     ## First generate latest student behavior data from event logs
#     subprocess.run(
#     [sys.executable, "student_behavior.py"]
#     )

#     # Run K-Means analysis
#     subprocess.run(
#         [sys.executable, "kmeans_analysis.py"]
#     )

#     students = []

#     try:
#         with open("student_clusters.csv", "r") as file:

#             reader = csv.DictReader(file)

#             for row in reader:
#                 students.append(row)

#     except FileNotFoundError:
#         students = []

#     # Count risk levels
#     low_risk = sum(
#         1 for student in students
#         if student["Risk_Level"] == "Low Risk"
#     )

#     medium_risk = sum(
#         1 for student in students
#         if student["Risk_Level"] == "Medium Risk"
#     )

#     high_risk = sum(
#         1 for student in students
#         if student["Risk_Level"] == "High Risk"
#     )

#     return render_template(
#         "invigilator.html",
#         students=students,
#         low_risk=low_risk,
#         medium_risk=medium_risk,
#         high_risk=high_risk
#     )




@app.route("/invigilator")
def invigilator():

    if "username" not in session:
        return redirect(url_for("login"))

    # -----------------------------------
    # Generate latest student behavior
    # -----------------------------------

    subprocess.run(
        [sys.executable, "student_behavior.py"]
    )


    # -----------------------------------
    # Run K-Means analysis
    # -----------------------------------

    subprocess.run(
        [sys.executable, "kmeans_analysis.py"]
    )


    # -----------------------------------
    # Read student cluster data
    # -----------------------------------

    students = []

    try:

        with open("student_clusters.csv", "r") as file:

            reader = csv.DictReader(file)

            for row in reader:

                students.append(row)

    except FileNotFoundError:

        students = []


    # -----------------------------------
    # Read exam results
    # -----------------------------------

    exam_scores = {}

    try:

        with open("exam_results.csv", "r") as file:

            reader = csv.DictReader(file)

            for row in reader:

                username = row["Username"]

                exam_scores[username] = (
                    row["Score"]
                    + "/"
                    + row["Total Questions"]
                )

    except FileNotFoundError:

        exam_scores = {}


    # -----------------------------------
    # Add exam score to each student
    # -----------------------------------

    for student in students:

        username = student["Username"]

        student["Exam_Score"] = exam_scores.get(
            username,
            "Not Submitted"
        )


    # -----------------------------------
    # Count risk levels
    # -----------------------------------

    low_risk = sum(
        1
        for student in students
        if student["Risk_Level"] == "Low Risk"
    )


    medium_risk = sum(
        1
        for student in students
        if student["Risk_Level"] == "Medium Risk"
    )


    high_risk = sum(
        1
        for student in students
        if student["Risk_Level"] == "High Risk"
    )


    # -----------------------------------
    # Analytics summary
    # -----------------------------------

    integrity_scores = []

    total_suspicious_events = 0

    for student in students:

        # Integrity score
        try:
            score = float(student["Integrity_Score"])

            integrity_scores.append(score)

        except (ValueError, TypeError):
            pass

        # Suspicious events
        try:
            total_suspicious_events += int(
                student["Total_Suspicious_Events"]
            )

        except (ValueError, TypeError):
            pass


    # Calculate average integrity score
    if integrity_scores:

        average_integrity = round(
            sum(integrity_scores) / len(integrity_scores),
            2
        )

    else:

        average_integrity = 0
        
        
        
        
    
    # -----------------------------------
    # Read incident evidence
    # -----------------------------------

    incidents = []

    conn = sqlite3.connect("examguard.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            event_type,
            details,
            timestamp,
            severity,
            screenshot_path
        FROM incidents
        ORDER BY id DESC
    """)

    for row in cursor.fetchall():

        incidents.append({
            "id": row[0],
            "username": row[1],
            "event_type": row[2],
            "details": row[3],
            "timestamp": row[4],
            "severity": row[5],
            "screenshot_path": row[6]
        })

    conn.close()


    # -----------------------------------
    # Send data to invigilator page
    # -----------------------------------

    return render_template(
        "invigilator.html",

        students=students,

        low_risk=low_risk,

        medium_risk=medium_risk,

        high_risk=high_risk,

        average_integrity=average_integrity,

        total_suspicious_events=total_suspicious_events,
        
        incidents=incidents
    )





@app.route("/evidence/<filename>")
def evidence(filename):

    return send_from_directory(
        "evidence",
        filename
    )







@app.route("/ai_report/<username>")
def ai_report(username):

    if "username" not in session:
        return redirect(url_for("login"))

    try:

        report = generate_ai_report(username)

        return render_template(
            "ai_report.html",
            username=username,
            report=report
        )

    except Exception as e:

        return f"Error generating AI report: {str(e)}"







# @app.route("/logout")
# def logout():

#     session.pop("username", None)

#     # return "Logged Out Successfully"
#     return redirect(url_for("home"))



@app.route("/logout")
def logout():
    
     
    reset_score()

    session.pop("username", None)

    session.pop("exam_session_start", None)

    return redirect(url_for("home"))




@app.route("/video_feed")
def video_feed():

    if "username" not in session:
        return "Unauthorized", 401

    username = session["username"]

    return Response(
        generate_monitoring_frames(username),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )
    
    
    
@app.route("/monitoring_status")
def monitoring_status():

    if "username" not in session:
        return {"status": "Unauthorized"}, 401

    return {
        "status": get_current_status(),
        "integrity_score": get_score()
    }


@app.route("/exam_result")
def exam_result():

    if "username" not in session:
        return redirect(url_for("login"))

    integrity_score = get_score()

    return render_template(
        "exam_result.html",
        username=session["username"],
        integrity_score=integrity_score
    )




@app.route("/submit_exam", methods=["POST"])
def submit_exam():

    if "username" not in session:
        return {"success": False}, 401

    username = session["username"]

    # Correct answers
    answer_key = {
        "q1": "TCP",
        "q2": "Inheritance",
        "q3": "Stack",
        "q4": "SELECT"
    }

    score = 0
    total_questions = len(answer_key)

    # Check answers
    for question, correct_answer in answer_key.items():

        student_answer = request.form.get(question)

        if student_answer == correct_answer:
            score += 1

    # Save result
    result_file = "exam_results.csv"

    file_exists = os.path.isfile(result_file)

    with open(result_file, "a", newline="") as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Username",
                "Score",
                "Total Questions",
                "Submitted At"
            ])

        writer.writerow([
            username,
            score,
            total_questions,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ])
        
        
        
        
            # -----------------------------------
    # End exam session
    # -----------------------------------

    session_start = session.get("exam_session_start")

    if session_start:

        session_file = "exam_sessions.csv"

        rows = []

        try:

            with open(session_file, "r", newline="") as file:

                reader = csv.DictReader(file)

                for row in reader:

                    if (
                        row["Username"] == username
                        and row["Start"] == session_start
                        and row["End"] == ""
                    ):

                        row["End"] = datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                    rows.append(row)


            with open(session_file, "w", newline="") as file:

                writer = csv.DictWriter(
                    file,
                    fieldnames=[
                        "Username",
                        "Start",
                        "End"
                    ]
                )

                writer.writeheader()
                writer.writerows(rows)

        except FileNotFoundError:
            pass


        # Remove session information
        session.pop("exam_session_start", None)
        

    return {
        "success": True,
        "score": score
    }





if __name__ == "__main__":
    app.run(debug=True)