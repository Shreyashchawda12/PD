import os
import matplotlib.pyplot as plt
import seaborn as sns

import pandas as pd

df = pd.read_excel("artifacts\clean_data.xlsx")

# Load the data into a DataFrame (assuming you've already read it into `df`)

# Convert 'Site Mins' column to numeric if not already
df["Site Mins"] = pd.to_numeric(df["Site Mins"], errors="coerce")

# Get top 5 Site Names per Cluster based on Site Mins
top_sites = df.groupby("Cluster", group_keys=False).apply(lambda x: x.nlargest(5, "Site Mins"))

# Selecting required columns
top_sites = top_sites[["CE", "Site Name",  "Site Mins"]]

# Display result
print(top_sites)

# Save to Excel (optional)
# top_sites.to_excel("top_5_sites_per_cluster.xlsx", index=False)


