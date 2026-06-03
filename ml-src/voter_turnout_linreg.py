import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

df = pd.read_csv("../datasets/eu_turnout_clean.csv")

# region mapping
region_map = {
    "BE": "Western", "FR": "Western", "DE": "Western", "NL": "Western",
    "LU": "Western", "AT": "Western", "IE": "Western",
    "SE": "Northern", "DK": "Northern", "FI": "Northern",
    "EE": "Northern", "LV": "Northern", "LT": "Northern",
    "PL": "Eastern", "CZ": "Eastern", "SK": "Eastern", "HU": "Eastern",
    "RO": "Eastern", "BG": "Eastern", "SI": "Eastern", "HR": "Eastern",
    "ES": "Southern", "PT": "Southern", "IT": "Southern",
    "EL": "Southern", "MT": "Southern", "CY": "Southern",
}
df["region"] = df["country"].map(region_map)
df = pd.get_dummies(df, columns=["region"], drop_first=True)
region_cols = [c for c in df.columns if c.startswith("region_")]

FEATURES = [
    "compulsory_voting",
    "median_age",
    "eu_net_beneficiary",
    "national_turnout",
    "weekend_voting",
    "gdp_per_capita",
    "unemployment_rate",
    "population",
] + region_cols
TARGET = "voter_turnout"

X = np.array(df[FEATURES])
y = np.array(df[TARGET])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# standardise
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

X_train_b = np.column_stack([np.ones(len(X_train_scaled)), X_train_scaled])
X_test_b  = np.column_stack([np.ones(len(X_test_scaled)),  X_test_scaled])

# line of best fit
b = np.linalg.inv(X_train_b.T @ X_train_b) @ (X_train_b.T @ y_train)

# predictions and residuals
y_hat_train = X_train_b @ b
y_hat_test  = X_test_b  @ b

res_train = y_hat_train - y_train
res_test  = y_hat_test  - y_test

# metrics
MSE_train = (res_train ** 2).mean()
MSE_test  = (res_test  ** 2).mean()
R2_train  = 1 - MSE_train / y_train.var()
R2_test   = 1 - MSE_test  / y_test.var()

print("OLS Linear Regression — EU Voter Turnout")
print("─" * 50)
print(f"  N train    : {len(y_train)}")
print(f"  N test     : {len(y_test)}")
print(f"  R² train   : {R2_train:.4f}")
print(f"  R² test    : {R2_test:.4f}")
print(f"  MSE train  : {MSE_train:.4f}")
print(f"  MSE test   : {MSE_test:.4f}")
print("─" * 50)
print(f"{'feature':<25} {'coef':>8}")
for name, coef in zip(["intercept"] + FEATURES, b):
    print(f"  {name:<23} {coef:>8.4f}")

# refit on full dataset for final coefficients
scaler_full = StandardScaler()
X_full_scaled = scaler_full.fit_transform(X)
X_full_b = np.column_stack([np.ones(len(X_full_scaled)), X_full_scaled])
b_full = np.linalg.inv(X_full_b.T @ X_full_b) @ (X_full_b.T @ y)

res_full = X_full_b @ b_full - y
MSE_full = (res_full ** 2).mean()
R2_full  = 1 - MSE_full / y.var()

print(f"\nFinal model (full dataset, N={len(y)})")
print("─" * 50)
print(f"  R²  : {R2_full:.4f}")
print(f"  MSE : {MSE_full:.4f}")
print("─" * 50)
print(f"{'feature':<25} {'coef':>8}")
for name, coef in zip(["intercept"] + FEATURES, b_full):
    print(f"  {name:<23} {coef:>8.4f}")