import pandas as pd

# from langchain_ollama import ChatOllama
# from langchain_core.prompts import ChatPromptTemplate



from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate


def generate_ai_report(student_name):



# ==========================================
# 1. LOAD EXAMGUARD DATA
# ==========================================

    behavior_df = pd.read_csv("student_behavior.csv")
    cluster_df = pd.read_csv("student_clusters.csv")
    events_df = pd.read_csv("event_logs.csv")
    sessions_df = pd.read_csv("exam_sessions.csv")

    print("ExamGuard data loaded successfully!")


    # ==========================================
    # 2. SELECT STUDENT
    # ==========================================

    # student_name = input(
    #     "\nEnter student name: "
    # ).strip()


    # Find student behavior data
    student_data = behavior_df[
        behavior_df["Username"].str.lower()
        == student_name.lower()
    ]


    if student_data.empty:

        print(
            f"\nStudent '{student_name}' not found."
        )

        exit()


    student = student_data.iloc[0]


    # ==========================================
    # 3. GET STUDENT INFORMATION
    # ==========================================

    username = student["Username"]

    face_absent = int(student["Face_Absent"])

    multiple_faces = int(
        student["Multiple_Faces"]
    )

    tab_switches = int(
        student["Tab_Switches"]
    )

    suspicious_events = int(
        student["Total_Suspicious_Events"]
    )

    presence_ratio = student[
        "Face_Presence_Ratio"
    ]

    if (
        pd.notna(presence_ratio)
        and str(presence_ratio).strip().lower()
        not in ["not available", "unavailable", ""]
    ):
        presence_percentage = round(
            float(presence_ratio) * 100, 2
        )
    else:
        presence_percentage = "Unavailable"


    integrity_score = float(
        student["Integrity_Score"]
    )


    # ==========================================
    # 4. GET OFFICIAL RISK LEVEL
    # ==========================================

    cluster_student = cluster_df[
        cluster_df["Username"].str.lower()
        == student_name.lower()
    ]


    if cluster_student.empty:

        print(
            f"\nRisk information for "
            f"'{student_name}' not found."
        )

        exit()


    risk_level = cluster_student.iloc[0][
        "Risk_Level"
    ]


    # ==========================================
    # 5. FIND LATEST EXAM SESSION
    # ==========================================

    student_sessions = sessions_df[
        sessions_df["Username"].str.lower()
        == student_name.lower()
    ].copy()


    if student_sessions.empty:

        print(
            f"\nNo exam session found for "
            f"'{student_name}'."
        )

        exit()


    student_sessions["Start_dt"] = pd.to_datetime(
        student_sessions["Start"],
        errors="coerce"
    )


    latest_session = (
        student_sessions
        .sort_values("Start_dt")
        .iloc[-1]
    )


    session_start = pd.to_datetime(
        latest_session["Start"],
        errors="coerce"
    )


    session_end = pd.to_datetime(
        latest_session["End"],
        errors="coerce"
    )


    # ==========================================
    # 6. GET EVENTS FROM THAT EXAM SESSION
    # ==========================================

    events_df["Timestamp_dt"] = pd.to_datetime(
        events_df["Timestamp"],
        errors="coerce"
    )


    student_events = events_df[
        (events_df["Username"].str.lower()
        == student_name.lower())
        &
        (events_df["Timestamp_dt"]
        >= session_start)
    ]


    # If session has ended,
    # restrict events to session end.

    if pd.notna(session_end):

        student_events = student_events[
            student_events["Timestamp_dt"]
            <= session_end
        ]


    # ==========================================
    # 7. FORMAT EVENT EVIDENCE
    # ==========================================

    if student_events.empty:

        event_evidence = (
            "No suspicious events were recorded "
            "during the latest exam session."
        )

    else:

        event_lines = []

        for _, event in student_events.iterrows():

            timestamp = event["Timestamp"]

            event_type = event["Event"]

            details = event["Details"]

            event_lines.append(
                f"- {timestamp} | "
                f"{event_type} | "
                f"{details}"
            )

        event_evidence = "\n".join(
            event_lines
        )


    # ==========================================
    # 8. CREATE LANGCHAIN PROMPT
    # ==========================================

    prompt = ChatPromptTemplate.from_messages(

        [

            (
                "system",

                """
    You are the AI Integrity Report Agent
    for ExamGuard, an online examination
    monitoring system.

    Your task is to summarize and explain
    the monitoring evidence provided by
    ExamGuard for an exam invigilator.

    STRICT EVIDENCE RULES:

    1. Use ONLY the information provided
    in the input.

    2. Never invent events, timestamps,
    durations, causes, or student actions.

    3. ExamGuard uses FACE DETECTION,
    not face recognition.
    Always use the term "face detection".

    4. A "Face Absent" event only means
    that the system did not detect a face.
    Do NOT state that the student left,
    cheated, or was using another resource.

    5. A "Tab Switched" event only means
    that a tab switch was detected.
    Do NOT claim that the student opened
    unauthorized resources or cheated.

    6. Never state or imply that an event
    proves academic misconduct.

    7. Do not invent explanations for why
    an event occurred.

    8. The Risk Level supplied by ExamGuard
    is the official risk classification.
    Do not change it.

    9. The Integrity Score supplied by
    ExamGuard is the official score.
    Do not recalculate it.

    10. Clearly separate:
        - Recorded Evidence
        - Assessment

    11. The Assessment must describe patterns
        in the recorded evidence without
        assuming the student's intention.

    12. If the evidence is insufficient to
        determine the cause of an event,
        explicitly say that the cause cannot
        be determined from the monitoring data.

    13. Recommendations should be limited to
        reviewing the recorded evidence when
        appropriate.
        
        
    14. Do not classify a face presence ratio as
        acceptable, normal, abnormal, sufficient,
        or insufficient unless ExamGuard explicitly
        provides such a threshold.

    15. Do not state that there is or is not a
        cause for concern. Simply describe the
        recorded evidence and the official risk
        classification.



    Use this structure:

    INTEGRITY REPORT

    Student:
    Risk Level:
    Integrity Score:
    Face Presence:

    Summary:
    Brief factual summary of the monitoring data.

    Recorded Evidence:
    List the actual events and their timestamps.

    Assessment:
    Explain the observed pattern using only
    the supplied evidence.

    Recommendation:
    Provide a cautious recommendation for
    the invigilator.
    """
            ),

            (
                "human",

                """
    Student: {username}

    Official Risk Level:
    {risk_level}

    Integrity Score:
    {integrity_score}

    Face Presence Ratio:
    {presence_ratio}

    Face Absent Events:
    {face_absent}

    Multiple Face Events:
    {multiple_faces}

    Tab Switch Events:
    {tab_switches}

    Total Suspicious Events:
    {suspicious_events}

    Recorded Event Log:
    {event_evidence}
    """
            )

        ]
    )


    # ==========================================
    # 9. CREATE LOCAL OLLAMA MODEL
    # ==========================================

    # llm = ChatOllama(

    #     model="qwen2.5:3b-instruct",

    #     temperature=0
    # )
    llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
    )

    # ==========================================
    # 10. CREATE LANGCHAIN CHAIN
    # ==========================================

    chain = prompt | llm


    # ==========================================
    # 11. GENERATE REPORT
    # ==========================================

    response = chain.invoke(

        {

            "username": username,

            "risk_level": risk_level,

            "integrity_score":
                integrity_score,

            "presence_ratio":
                presence_percentage,

            "face_absent":
                face_absent,

            "multiple_faces":
                multiple_faces,

            "tab_switches":
                tab_switches,

            "suspicious_events":
                suspicious_events,

            "event_evidence":
                event_evidence

        }
    )
    # return response.content
    
    if isinstance(response.content, list):
        report = "\n".join(
            block["text"]
            for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    else:
        report = response.content

    return report
        
    
    
    

# ==========================================
# 12. DISPLAY REPORT
# ==========================================

# print("\n")

# print("=" * 70)

# print("EXAMGUARD AI INTEGRITY REPORT")

# print("=" * 70)

# print()

# # print(response.content)


# print()

# print("=" * 70)



if __name__ == "__main__":

    student_name = input(
        "\nEnter student name: "
    ).strip()

    print("\n")
    print("=" * 70)
    print("EXAMGUARD AI INTEGRITY REPORT")
    print("=" * 70)
    print()

    print(
        generate_ai_report(student_name)
    )

    print()
    print("=" * 70)