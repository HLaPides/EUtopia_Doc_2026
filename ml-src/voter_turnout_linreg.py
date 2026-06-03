""" 
linear regression model predicting EU voter turnout.

Features:
  - compulsory_voting     : binary, whether voting is legally required
  - median_age            : median age of the population
  - median_age_sq         : median age squared. relationship isn't linear, its closer to a parabola than a line so we sqaured it
  - national_turnout      : national election turnout (%)
  - national_turnout_sq   : national election turnout squared, same reasoning as median_age_sq
  - unemployment_rate     : unemployment rate (%)
  - population            : country population
  - compulsory_x_western  : interaction between compulsory voting and Western region
                            compulsory voting is only meaningfully enforced in Western
                            Europe (Belgium and Luxembourg); Greece has
                            compulsory voting on paper but don't do much to enforece it
  - region_northern/
    southern/western      : region binary columns with Eastern Europe as the reference
                            category. regional effects capture structural differences
                            in EU engagement not explained by the other features.
                            Eastern Europe averages around 20pp lower turnout than Western

Model is fit on an 80/20 train/test split (random_state=42). LOO-CV is used as the
primary performance metric.

Final performance: LOO-CV R²=0.7928, MSE=77.61
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

df = pd.read_csv("../datasets/eu_turnout_clean.csv")

df["national_turnout_sq"]  = df["national_turnout"] ** 2
df["log_unemployment_rate"] = np.log(df["unemployment_rate"])
df["median_age_sq"]        = df["median_age"] ** 2
df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

FEATURES = [
    "compulsory_voting",
    "median_age",
    "median_age_sq",
    "national_turnout",
    "national_turnout_sq",
    "log_unemployment_rate",
    "unemployment_rate",
    "population",
    "compulsory_x_western",
    "region_northern",
    "region_southern",
    "region_western",
]
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

# metrics
MSE_train = ((y_hat_train - y_train) ** 2).mean()
MSE_test  = ((y_hat_test  - y_test)  ** 2).mean()
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
print(f"\n{'feature':<25} {'coef':>8}")
print("─" * 50)
for name, coef in zip(["intercept"] + FEATURES, b):
    print(f"  {name:<23} {coef:>8.4f}")

# LOO used because its a relatively small dataset
scaler_loo = StandardScaler()
X_loo_scaled = scaler_loo.fit_transform(X)
y_loo = np.empty(len(y))
for obs in range(len(y)):
    X_loo = np.concatenate([X_loo_scaled[:obs], X_loo_scaled[obs+1:]])
    y_loo_train = np.concatenate([y[:obs], y[obs+1:]])
    X_loo_b = np.column_stack([np.ones(len(X_loo)), X_loo])
    b_loo = np.linalg.inv(X_loo_b.T @ X_loo_b) @ (X_loo_b.T @ y_loo_train)
    y_loo[obs] = np.array([1, *X_loo_scaled[obs]]) @ b_loo

MSE_loo = ((y_loo - y) ** 2).mean()
R2_loo  = 1 - MSE_loo / y.var()

print(f"\nLOO-CV R²  : {R2_loo:.4f}")
print(f"LOO-CV MSE : {MSE_loo:.4f}")