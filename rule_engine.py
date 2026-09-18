# rule_engine.py

# Initial Integrity Score
integrity_score = 100


# Penalty Rules
PENALTIES = {

    "Face Absent": 10,
    "Multiple Faces": 20,
    "Tab Switched": 15,
    "Window Minimized": 10

}


def deduct_marks(event):

    global integrity_score

    if event in PENALTIES:

        integrity_score -= PENALTIES[event]

    if integrity_score < 0:
        integrity_score = 0

    return integrity_score


def get_score():

    return integrity_score


def reset_score():

    global integrity_score

    integrity_score = 100