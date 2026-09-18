# import cv2
# from datetime import datetime

# from event_logger import log_event
# from rule_engine import deduct_marks

# # Open Camera
# camera = cv2.VideoCapture(0)

# # Load Haar Cascade
# face_detector = cv2.CascadeClassifier(
#     cv2.data.haarcascades +
#     "haarcascade_frontalface_default.xml"
# )

# # Threshold for absence
# FACE_ABSENCE_THRESHOLD = 2

# # Variables
# previous_status = None
# face_absent_start = None
# absence_logged = False

# while True:

#     success, frame = camera.read()

#     if not success:
#         break

#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     faces = face_detector.detectMultiScale(
#         gray,
#         scaleFactor=1.1,
#         minNeighbors=5,
#         minSize=(50, 50)
#     )

#     # ----------------------------
#     # Determine Current Status
#     # ----------------------------

#     if len(faces) == 0:
#         status = "No Face Detected"

#     elif len(faces) == 1:
#         status = "Student Present"

#     else:
#         status = "Multiple Faces Detected"

#     # ----------------------------
#     # Status Change Handling
#     # ----------------------------

#     if status != previous_status:

#         if status == "No Face Detected":

#             # Start absence timer
#             face_absent_start = datetime.now()

#         elif status == "Student Present":

#             # Student returned after absence
#             if face_absent_start is not None and absence_logged:

#                 duration = (
#                     datetime.now() - face_absent_start
#                 ).total_seconds()

#                 log_event(
#                     "Face Present",
#                     f"Student returned after {duration:.1f} seconds"
#                 )

#             face_absent_start = None
#             absence_logged = False

#         elif status == "Multiple Faces Detected":

#             log_event(
#                 "Multiple Faces",
#                 "More than one face detected"
#             )

#             deduct_marks("Multiple Faces")

#             # Reset absence tracking
#             face_absent_start = None
#             absence_logged = False

#         previous_status = status

#     # ----------------------------
#     # Face Absence Threshold
#     # ----------------------------

#     if (
#         status == "No Face Detected"
#         and face_absent_start is not None
#         and not absence_logged
#     ):

#         elapsed = (
#             datetime.now() - face_absent_start
#         ).total_seconds()

#         if elapsed >= FACE_ABSENCE_THRESHOLD:

#             log_event(
#                 "Face Absent",
#                 "No face detected"
#             )

#             deduct_marks("Face Absent")

#             absence_logged = True

#     # ----------------------------
#     # Draw Face Rectangles
#     # ----------------------------

#     for (x, y, w, h) in faces:

#         cv2.rectangle(
#             frame,
#             (x, y),
#             (x + w, y + h),
#             (0, 255, 0),
#             2
#         )

#     # ----------------------------
#     # Display Status
#     # ----------------------------

#     cv2.putText(
#         frame,
#         status,
#         (20, 40),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         1,
#         (0, 0, 255),
#         2
#     )

#     cv2.imshow("ExamGuard", frame)

#     if cv2.waitKey(1) == ord('q'):
#         break

# camera.release()
# cv2.destroyAllWindows()













#second

import sys
import cv2
from datetime import datetime

from event_logger import log_event
from rule_engine import deduct_marks

from incident_logger import log_incident

username = sys.argv[1]

# -----------------------------
# Camera Setup
# -----------------------------

camera = cv2.VideoCapture(0)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# -----------------------------
# Thresholds
# -----------------------------

FACE_ABSENCE_THRESHOLD = 2
MULTIPLE_FACE_THRESHOLD = 1.5


# -----------------------------
# Tracking Variables
# -----------------------------

previous_status = None

# Face absence tracking
face_absent_start = None
absence_logged = False

# Multiple face tracking
multiple_faces_start = None
multiple_faces_logged = False


# --------------------------------
# Face presence duration tracking
# --------------------------------

monitoring_start = datetime.now()

face_present_start = None
total_face_present_duration = 0.0

face_absent_duration = 0.0
multiple_face_duration = 0.0




# -----------------------------
# Main Camera Loop
# -----------------------------

while True:

    success, frame = camera.read()

    if not success:
        break


    # Convert frame to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # -----------------------------
    # Detect Faces
    # -----------------------------

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=7,
        minSize=(60, 60)
    )


    # -----------------------------
    # Determine Status
    # -----------------------------

    if len(faces) == 0:

        status = "No Face Detected"

    elif len(faces) == 1:

        status = "Student Present"

    else:

        status = "Multiple Faces Detected"
        
    
    current_time = datetime.now()
    
    
    
    
    # =================================================
    # FACE PRESENCE DURATION TRACKING
    # =================================================

    if status == "Student Present":

        # Start counting present time
        if face_present_start is None:
            face_present_start = current_time


    elif status == "No Face Detected":

        # Student is no longer present
        if face_present_start is not None:

            duration = (
                current_time - face_present_start
            ).total_seconds()

            total_face_present_duration += duration

            face_present_start = None


    elif status == "Multiple Faces Detected":

        # Student-present interval ends
        if face_present_start is not None:

            duration = (
                current_time - face_present_start
            ).total_seconds()

            total_face_present_duration += duration

            face_present_start = None
        


    # =================================================
    # FACE ABSENCE TRACKING
    # =================================================

    if status == "No Face Detected":

        # Start absence timer
        if face_absent_start is None:

            face_absent_start = datetime.now()


        # Check how long face has been absent
        elapsed = (
            datetime.now() - face_absent_start
        ).total_seconds()


        # Log only after threshold is crossed
        if (
            elapsed >= FACE_ABSENCE_THRESHOLD
            and not absence_logged
        ):

            log_event(
                "Face Absent",
                "No face detected",
                username
            )
            
            log_incident(
                username,
                "Face Absent",
                "No face detected",
                "Medium"
            )

            deduct_marks("Face Absent")

            absence_logged = True


    else:

        # Face is detected again
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


        # Reset absence tracking
        # Because the previous absence incident is finished.
        face_absent_start = None
        absence_logged = False


    # =================================================
    # MULTIPLE FACE TRACKING
    # =================================================

    if status == "Multiple Faces Detected":

        # Start multiple-face timer
        if multiple_faces_start is None:

            multiple_faces_start = datetime.now()


        # Calculate duration
        elapsed = (
            datetime.now() - multiple_faces_start
        ).total_seconds()


        # Log only if multiple faces persist
        if (
            elapsed >= MULTIPLE_FACE_THRESHOLD
            and not multiple_faces_logged
        ):

            log_event(
                "Multiple Faces",
                "More than one face detected",
                username
            )
            
            log_incident(
                username,
                "Multiple Faces",
                "More than one face detected",
                "High"
            )

            deduct_marks("Multiple Faces")

            multiple_faces_logged = True


    else:

        # Multiple faces disappeared
        multiple_faces_start = None
        multiple_faces_logged = False


    # =================================================
    # DRAW FACE RECTANGLES
    # =================================================

    for (x, y, w, h) in faces:

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )


    # =================================================
    # DISPLAY STATUS
    # =================================================

    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),                  # represents green in OpenCV's BGR format
        2                             # thickness of rectangular border
    )


    # Show camera
    cv2.imshow(
        "ExamGuard",
        frame
    )


    # Press Q to exit
    if cv2.waitKey(1) == ord('q'):
        break






# =================================================
# FINAL FACE PRESENCE CALCULATION
# =================================================

monitoring_end = datetime.now()

# If student is still present when monitoring ends,
# close the final presence interval.
if face_present_start is not None:

    duration = (
        monitoring_end - face_present_start
    ).total_seconds()

    total_face_present_duration += duration

# Total monitoring duration
total_monitoring_duration = (
    monitoring_end - monitoring_start
).total_seconds()

# Calculate presence ratio
if total_monitoring_duration > 0:

    face_presence_ratio = (
        total_face_present_duration
        / total_monitoring_duration
    ) * 100

else:

    face_presence_ratio = 0


print("-----------------------------------")
print("Face Presence Analysis")
print("-----------------------------------")
print(
    f"Monitoring Duration: "
    f"{total_monitoring_duration:.1f} seconds"
)
print(
    f"Face Present Duration: "
    f"{total_face_present_duration:.1f} seconds"
)
print(
    f"Face Presence Ratio: "
    f"{face_presence_ratio:.2f}%"
)




# -----------------------------
# Release Camera
# -----------------------------

camera.release()

cv2.destroyAllWindows()