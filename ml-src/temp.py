import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import json

FEATURES = [
    "compulsory_voting", "median_age", "median_age_sq",
    "national_turnout", "national_turnout_sq", "unemployment_rate",
    "population", "compulsory_x_western", "region_northern",
    "region_southern", "region_western",
]

df = pd.read_csv("../datasets/eu_turnout_clean.csv")
df["median_age_sq"]        = df["median_age"] ** 2
df["national_turnout_sq"]  = df["national_turnout"] ** 2
df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

X = df[FEATURES].values
y = df["voter_turnout"].values

scaler   = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_b      = np.column_stack([np.ones(len(X_scaled)), X_scaled])
b        = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)

print("beta_vals:", json.dumps(b.tolist()))
print("feature_means:", json.dumps(scaler.mean_.tolist()))
print("feature_stds:", json.dumps(scaler.scale_.tolist()))