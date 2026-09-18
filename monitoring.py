# import cv2
# from datetime import datetime

# from event_logger import log_event
# from rule_engine import deduct_marks


# FACE_ABSENCE_THRESHOLD = 2
# MULTIPLE_FACE_THRESHOLD = 1.5



# current_status = "Starting Monitoring"


# def get_current_status():
#     return current_status


# face_detector = cv2.CascadeClassifier(
#     cv2.data.haarcascades +
#     "haarcascade_frontalface_default.xml"
# )


# def generate_monitoring_frames(username):

#     camera = cv2.VideoCapture(0)

#     previous_status = None

#     face_absent_start = None
#     absence_logged = False

#     multiple_face_start = None
#     multiple_face_logged = False

#     while True:

#         success, frame = camera.read()

#         if not success:
#             break


#         # -----------------------------
#         # FACE DETECTION
#         # -----------------------------

#         gray = cv2.cvtColor(
#             frame,
#             cv2.COLOR_BGR2GRAY
#         )

#         faces = face_detector.detectMultiScale(
#             gray,
#             scaleFactor=1.1,
#             minNeighbors=5,
#             minSize=(50, 50)
#         )


#         # -----------------------------
#         # DETERMINE STATUS
#         # -----------------------------

#         if len(faces) == 0:

#             status = "No Face Detected"

#         elif len(faces) == 1:

#             status = "Student Present"

#         else:

#             status = "Multiple Faces Detected"
            
#         global current_status

#         current_status = status


#         # -----------------------------
#         # FACE ABSENCE
#         # -----------------------------

#         if status != previous_status:

#             if status == "No Face Detected":

#                 face_absent_start = datetime.now()

#         elif status == "Student Present":

#             if (
#                 face_absent_start is not None
#                 and absence_logged
#             ):

#                 duration = (
#                     datetime.now() - face_absent_start
#                 ).total_seconds()

#                 log_event(
#                     "Face Present",
#                     f"Student returned after {duration:.1f} seconds",
#                     username
#                 )

#             face_absent_start = None
#             absence_logged = False


#         previous_status = status


#         # -----------------------------
#         # LOG FACE ABSENCE
#         # -----------------------------

#         if (
#             status == "No Face Detected"
#             and face_absent_start is not None
#             and not absence_logged
#         ):

#             elapsed = (
#                 datetime.now() - face_absent_start
#             ).total_seconds()

#             if elapsed >= FACE_ABSENCE_THRESHOLD:

#                 log_event(
#                     "Face Absent",
#                     "No face detected",
#                     username
#                 )

#                 deduct_marks("Face Absent")

#                 absence_logged = True


#         # -----------------------------
#         # MULTIPLE FACE DETECTION
#         # -----------------------------

#         if len(faces) > 1:

#             if multiple_face_start is None:

#                 multiple_face_start = datetime.now()

#             elif not multiple_face_logged:

#                 duration = (
#                     datetime.now() - multiple_face_start
#                 ).total_seconds()

#                 if duration >= MULTIPLE_FACE_THRESHOLD:

#                     log_event(
#                         "Multiple Faces",
#                         "More than one face detected",
#                         username
#                     )

#                     deduct_marks(
#                         "Multiple Faces"
#                     )

#                     multiple_face_logged = True

#         else:

#             multiple_face_start = None
#             multiple_face_logged = False


#         # -----------------------------
#         # DRAW FACE RECTANGLES
#         # -----------------------------

#         for (x, y, w, h) in faces:

#             cv2.rectangle(
#                 frame,
#                 (x, y),
#                 (x + w, y + h),
#                 (0, 255, 0),
#                 2
#             )


#         # -----------------------------
#         # DISPLAY STATUS
#         # -----------------------------

#         if status == "Student Present":

#             status_color = (0, 255, 0)

#         elif status == "No Face Detected":

#             status_color = (0, 0, 255)

#         else:

#             status_color = (0, 165, 255)


#         # Background rectangle for status
#         cv2.rectangle(
#             frame,
#             (10, 10),
#             (330, 60),
#             (0, 0, 0),
#             -1
#         )


#         # Status text
#         cv2.putText(
#             frame,
#             status,
#             (20, 45),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.9,
#             status_color,
#             2
#         )


#         # -----------------------------
#         # CONVERT FRAME FOR BROWSER
#         # -----------------------------

#         ret, buffer = cv2.imencode(
#             ".jpg",
#             frame
#         )

#         if not ret:
#             continue

#         frame_bytes = buffer.tobytes()


#         yield (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n\r\n"
#             + frame_bytes
#             + b"\r\n"
#         )


#     camera.release()










































import cv2
import csv
import os
import time
from datetime import datetime

from event_logger import log_event
from rule_engine import deduct_marks


FACE_ABSENCE_THRESHOLD = 2
MULTIPLE_FACE_THRESHOLD = 1.5


# Time-based face presence data
FACE_PRESENCE_FILE = "face_presence.csv"


def _ensure_presence_file():
    if not os.path.exists(FACE_PRESENCE_FILE):
        with open(FACE_PRESENCE_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                "Username", "Face_Present_Seconds",
                "Face_Absent_Seconds", "Presence_Ratio"
            ])


def _save_presence_data(username, present_seconds, absent_seconds):
    _ensure_presence_file()
    total_seconds = present_seconds + absent_seconds
    ratio = present_seconds / total_seconds if total_seconds > 0 else 1.0

    rows = []
    found = False
    with open(FACE_PRESENCE_FILE, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["Username"] == username:
                row["Face_Present_Seconds"] = f"{present_seconds:.1f}"
                row["Face_Absent_Seconds"] = f"{absent_seconds:.1f}"
                row["Presence_Ratio"] = f"{ratio:.4f}"
                found = True
            rows.append(row)

    if not found:
        rows.append({
            "Username": username,
            "Face_Present_Seconds": f"{present_seconds:.1f}",
            "Face_Absent_Seconds": f"{absent_seconds:.1f}",
            "Presence_Ratio": f"{ratio:.4f}"
        })

    with open(FACE_PRESENCE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Username", "Face_Present_Seconds",
            "Face_Absent_Seconds", "Presence_Ratio"
        ])
        writer.writeheader()
        writer.writerows(rows)



current_status = "Starting Monitoring"


def get_current_status():
    return current_status


face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


def generate_monitoring_frames(username):

    # camera = cv2.VideoCapture(0)
    camera = cv2.VideoCapture(
    0,
    cv2.CAP_DSHOW
    )
    
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    if not camera.isOpened():
        print("ERROR: Unable to open camera")
        return

    previous_status = None

    face_absent_start = None
    absence_logged = False

    multiple_face_start = None
    multiple_face_logged = False

    # Genuine time-based face presence tracking
    last_status_time = datetime.now()
    present_seconds = 0.0
    absent_seconds = 0.0
    
    last_save_time = datetime.now()
    
    frame_count = 0
    faces = []

    while True:

        success, frame = camera.read()

        if not success:
            break


        # -----------------------------
        # FACE DETECTION
        # -----------------------------

        frame_count += 1

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Detect faces only every 3rd frame
        if frame_count % 3 == 0:

            faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 50)
            )


        # -----------------------------
        # DETERMINE STATUS
        # -----------------------------

        if len(faces) == 0:

            status = "No Face Detected"

        elif len(faces) == 1:

            status = "Student Present"

        else:

            status = "Multiple Faces Detected"
            
        global current_status

        current_status = status

        # Accumulate time spent in the previous face state.
        now = datetime.now()
        interval = (now - last_status_time).total_seconds()

        if previous_status == "Student Present":
            present_seconds += interval
        elif previous_status in ("No Face Detected", "Multiple Faces Detected"):
            absent_seconds += interval

        last_status_time = now

       # Save presence data once every second
        if (now - last_save_time).total_seconds() >= 2:
            _save_presence_data(
                username,
                present_seconds,
                absent_seconds
            )
            last_save_time = now

        # -----------------------------
        # FACE ABSENCE
        # -----------------------------

        if status != previous_status:

            if status == "No Face Detected":

                face_absent_start = datetime.now()

        elif status == "Student Present":

            if (
                face_absent_start is not None
                and absence_logged
            ):

                duration = (
                    datetime.now() - face_absent_start
                ).total_seconds()

                log_event(
                    "Face Present",
                    f"Student returned after {duration:.1f} seconds",
                    username
                )

            face_absent_start = None
            absence_logged = False


        previous_status = status


        # -----------------------------
        # LOG FACE ABSENCE
        # -----------------------------

        if (
            status == "No Face Detected"
            and face_absent_start is not None
            and not absence_logged
        ):

            elapsed = (
                datetime.now() - face_absent_start
            ).total_seconds()

            if elapsed >= FACE_ABSENCE_THRESHOLD:

                log_event(
                    "Face Absent",
                    "No face detected",
                    username
                )

                deduct_marks("Face Absent")

                absence_logged = True


        # -----------------------------
        # MULTIPLE FACE DETECTION
        # -----------------------------

        if len(faces) > 1:

            if multiple_face_start is None:

                multiple_face_start = datetime.now()

            elif not multiple_face_logged:

                duration = (
                    datetime.now() - multiple_face_start
                ).total_seconds()

                if duration >= MULTIPLE_FACE_THRESHOLD:

                    log_event(
                        "Multiple Faces",
                        "More than one face detected",
                        username
                    )

                    deduct_marks(
                        "Multiple Faces"
                    )

                    multiple_face_logged = True

        else:

            multiple_face_start = None
            multiple_face_logged = False


        # -----------------------------
        # DRAW FACE RECTANGLES
        # -----------------------------

        for (x, y, w, h) in faces:

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )


        # -----------------------------
        # DISPLAY STATUS
        # -----------------------------

        if status == "Student Present":

            status_color = (0, 255, 0)

        elif status == "No Face Detected":

            status_color = (0, 0, 255)

        else:

            status_color = (0, 165, 255)


        # Background rectangle for status
        cv2.rectangle(
            frame,
            (10, 10),
            (330, 60),
            (0, 0, 0),
            -1
        )


        # Status text
        cv2.putText(
            frame,
            status,
            (20, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            status_color,
            2
        )


        # -----------------------------
        # CONVERT FRAME FOR BROWSER
        # -----------------------------

        ret, buffer = cv2.imencode(
            ".jpg",
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 70]
        )

        if not ret:
            continue

        frame_bytes = buffer.tobytes()


        time.sleep(0.03)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes
            + b"\r\n"
        )


# Finalize the last status interval
    final_time = datetime.now()
    interval = (final_time - last_status_time).total_seconds()

    if previous_status == "Student Present":
        present_seconds += interval
    elif previous_status in ("No Face Detected", "Multiple Faces Detected"):
        absent_seconds += interval

    _save_presence_data(username, present_seconds, absent_seconds)

    camera.release()