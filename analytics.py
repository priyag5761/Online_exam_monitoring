import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------------
# 1. Load student behavior data
# -----------------------------------

DATA_FILE = "student_behavior.csv"
OUTPUT_DIR = "static"

os.makedirs(OUTPUT_DIR, exist_ok=True)

data = pd.read_csv(DATA_FILE)


# -----------------------------------
# 2. Basic validation
# -----------------------------------

required_columns = [
    "Username",
    "Face_Absent",
    "Multiple_Faces",
    "Tab_Switches",
    "Total_Suspicious_Events",
    "Integrity_Score"
]

for column in required_columns:

    if column not in data.columns:

        raise ValueError(
            f"Missing required column: {column}"
        )


print("\nAnalytics dataset loaded successfully!\n")

print(data)


# -----------------------------------
# 3. Integrity Score Distribution
# -----------------------------------

plt.figure(figsize=(9, 6))

sns.histplot(
    data["Integrity_Score"],
    bins=10,
    kde=True
)

plt.xlabel("Integrity Score")
plt.ylabel("Number of Students")
plt.title("Integrity Score Distribution")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "integrity_score_distribution.png"
    ),
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(
    "Integrity score distribution saved."
)


# -----------------------------------
# 4. Event Frequency
# -----------------------------------

event_counts = {
    "Face Absent": data["Face_Absent"].sum(),
    "Multiple Faces": data["Multiple_Faces"].sum(),
    "Tab Switches": data["Tab_Switches"].sum()
}

event_df = pd.DataFrame(
    list(event_counts.items()),
    columns=["Event", "Count"]
)


plt.figure(figsize=(9, 6))

sns.barplot(
    data=event_df,
    x="Event",
    y="Count"
)

plt.xlabel("Suspicious Event")
plt.ylabel("Frequency")
plt.title("Suspicious Event Frequency")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "event_frequency.png"
    ),
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(
    "Event frequency chart saved."
)


# -----------------------------------
# 5. Event Frequency Heatmap
# -----------------------------------

heatmap_data = data[
    [
        "Username",
        "Face_Absent",
        "Multiple_Faces",
        "Tab_Switches"
    ]
].set_index("Username")


plt.figure(figsize=(9, 6))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="YlOrRd"
)

plt.xlabel("Event Type")
plt.ylabel("Student")
plt.title("Student Event Frequency Heatmap")

plt.tight_layout()

plt.savefig(
    os.path.join(
        OUTPUT_DIR,
        "event_frequency_heatmap.png"
    ),
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print(
    "Event frequency heatmap saved."
)


# -----------------------------------
# 6. Cohort Risk Profiling
# -----------------------------------

# Use existing K-Means risk classification
# if available.

try:

    cluster_data = pd.read_csv(
        "student_clusters.csv"
    )

    if "Risk_Level" in cluster_data.columns:

        risk_counts = (
            cluster_data["Risk_Level"]
            .value_counts()
            .reindex(
                [
                    "Low Risk",
                    "Medium Risk",
                    "High Risk"
                ],
                fill_value=0
            )
        )

    else:

        raise FileNotFoundError


except FileNotFoundError:

    print(
        "\nstudent_clusters.csv not found."
    )

    print(
        "Skipping cohort risk profiling."
    )

    risk_counts = None


if risk_counts is not None:

    plt.figure(figsize=(9, 6))

    sns.barplot(
        x=risk_counts.index,
        y=risk_counts.values
    )

    plt.xlabel("Risk Level")
    plt.ylabel("Number of Students")
    plt.title("Cohort Risk Profile")

    plt.tight_layout()

    plt.savefig(
        os.path.join(
            OUTPUT_DIR,
            "cohort_risk_profile.png"
        ),
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(
        "Cohort risk profile saved."
    )


# -----------------------------------
# 7. Display summary
# -----------------------------------

print("\n===================================")
print("Analytics Summary")
print("===================================")

print("\nAverage Integrity Score:")

print(
    round(
        data["Integrity_Score"].mean(),
        2
    )
)


print("\nTotal Suspicious Events:")

print(
    data["Total_Suspicious_Events"].sum()
)


print("\nEvent Frequency:")

print(event_df)


if risk_counts is not None:

    print("\nCohort Risk Profile:")

    print(risk_counts)


print(
    "\nAnalytics module completed successfully!"
)