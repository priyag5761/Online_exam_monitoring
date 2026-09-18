import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# -----------------------------------
# 1. Load student behavior data
# -----------------------------------

data = pd.read_csv("student_behavior.csv")


# -----------------------------------
# 2. Select behavioral features
# -----------------------------------

features = [
    "Face_Absent",
    "Multiple_Faces",
    "Tab_Switches",
    "Total_Suspicious_Events"
]

X = data[features]


# -----------------------------------
# 3. Scale the features
# -----------------------------------

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# -----------------------------------
# 4. Apply K-Means
# -----------------------------------

# kmeans = KMeans(
#     n_clusters=3,
#     random_state=42,
#     n_init=10
# )



# -----------------------------------
# Determine number of clusters
# -----------------------------------

number_of_students = len(data)

if number_of_students >= 3:

    number_of_clusters = 3

elif number_of_students == 2:

    number_of_clusters = 2

else:

    number_of_clusters = 1


kmeans = KMeans(
    n_clusters=number_of_clusters,
    random_state=42,
    n_init=10
)





data["Cluster"] = kmeans.fit_predict(X_scaled)


# -----------------------------------
# 5. Analyze each cluster
# -----------------------------------

cluster_summary = data.groupby("Cluster")[features].mean()

print("\nCluster Summary:")
print(cluster_summary)


# -----------------------------------
# 6. Assign risk levels
# -----------------------------------

# cluster_summary["Risk_Score"] = (
#     cluster_summary["Face_Absent"]
#     + cluster_summary["Multiple_Faces"]
#     + cluster_summary["Tab_Switches"]
# )


# # Sort clusters from lowest to highest risk
# sorted_clusters = cluster_summary["Risk_Score"].sort_values().index


# risk_labels = {}

# risk_names = [
#     "Low Risk",
#     "Medium Risk",
#     "High Risk"
# ]

# risk_names = risk_names[:number_of_clusters]

# for cluster, risk in zip(sorted_clusters, risk_names):
#     risk_labels[cluster] = risk


# data["Risk_Level"] = data["Cluster"].map(risk_labels)




# -----------------------------------
# 6. Assign final risk levels
# -----------------------------------

def assign_risk_level(score):

    if score >= 80:
        return "Low Risk"

    elif score >= 60:
        return "Medium Risk"

    else:
        return "High Risk"


data["Risk_Level"] = data["Integrity_Score"].apply(
    assign_risk_level
)






# -----------------------------------
# 7. Display results
# -----------------------------------

print("\nStudent Risk Classification:")
print(
    data[
        [
            "Username",
            "Face_Absent",
            "Multiple_Faces",
            "Tab_Switches",
            "Integrity_Score",
            "Cluster",
            "Risk_Level"
        ]
    ]
)


# -----------------------------------
# 8. Save results
# -----------------------------------

data.to_csv(
    "student_clusters.csv",
    index=False
)

print("\nCluster results saved to student_clusters.csv")


# -----------------------------------
# 9. Visualization
# -----------------------------------

# plt.figure(figsize=(8, 6))

# for cluster in sorted(data["Cluster"].unique()):

#     cluster_data = data[
#         data["Cluster"] == cluster
#     ]

#     plt.scatter(
#         cluster_data["Tab_Switches"],
#         cluster_data["Face_Absent"],
#         label=risk_labels[cluster],
#         s=100
#     )


# # Add student names
# for _, row in data.iterrows():

#     plt.annotate(
#         row["Username"],
#         (
#             row["Tab_Switches"],
#             row["Face_Absent"]
#         ),
#         xytext=(5, 5),
#         textcoords="offset points"
#     )


# plt.xlabel("Number of Tab Switches")
# plt.ylabel("Number of Face-Absent Events")
# plt.title("ExamGuard Student Behavior Clusters")

# plt.legend()
# plt.grid(True)

# plt.tight_layout()

# plt.show()








# -----------------------------------
# 9. PCA Visualization
# -----------------------------------

from sklearn.decomposition import PCA

pca = PCA(n_components=2)

X_pca = pca.fit_transform(X_scaled)

data["PCA1"] = X_pca[:, 0]
data["PCA2"] = X_pca[:, 1]


plt.figure(figsize=(9, 6))

for cluster in sorted(data["Cluster"].unique()):

    cluster_data = data[
        data["Cluster"] == cluster
    ]

    plt.scatter(
        cluster_data["PCA1"],
        cluster_data["PCA2"],
        label=risk_labels[cluster],
        s=120
    )


# Add student names
for _, row in data.iterrows():

    plt.annotate(
        row["Username"],
        (row["PCA1"], row["PCA2"]),
        xytext=(6, 6),
        textcoords="offset points"
    )


plt.xlabel("PCA Component 1")
plt.ylabel("PCA Component 2")

plt.title("ExamGuard Student Behavior Clusters")

plt.legend()
plt.grid(True)

plt.tight_layout()

# plt.show()
plt.savefig(
    "static/kmeans_clusters.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()

print("K-Means visualization saved to static/kmeans_clusters.png")