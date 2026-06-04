import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

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

_model = None
_scaler = None


def train_model():
    global _model, _scaler

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    csv_path = os.path.join(base_dir, "datasets", "eu_turnout_clean.csv")

    df = pd.read_csv(csv_path)

    df["national_turnout_sq"] = df["national_turnout"] ** 2
    df["log_unemployment_rate"] = np.log(df["unemployment_rate"])
    df["median_age_sq"] = df["median_age"] ** 2
    df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

    X = np.array(df[FEATURES])
    y = np.array(df[TARGET])

    _scaler = StandardScaler()
    X_scaled = _scaler.fit_transform(X)
    X_b = np.column_stack([np.ones(len(X_scaled)), X_scaled])

    _model = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)


def predict_turnout(data):
    global _model, _scaler

    if _model is None:
        train_model()

    row = {
        "compulsory_voting": int(data.get("compulsory_voting", 0)),
        "median_age": float(data.get("median_age")),
        "national_turnout": float(data.get("national_turnout")),
        "unemployment_rate": float(data.get("unemployment_rate")),
        "population": float(data.get("population")),
        "region_northern": int(data.get("region_northern", 0)),
        "region_southern": int(data.get("region_southern", 0)),
        "region_western": int(data.get("region_western", 0)),
    }

    row["median_age_sq"] = row["median_age"] ** 2
    row["national_turnout_sq"] = row["national_turnout"] ** 2
    row["log_unemployment_rate"] = np.log(row["unemployment_rate"])
    row["compulsory_x_western"] = row["compulsory_voting"] * row["region_western"]

    X = np.array([[row[feature] for feature in FEATURES]])
    X_scaled = _scaler.transform(X)
    X_b = np.column_stack([np.ones(len(X_scaled)), X_scaled])

    prediction = float(X_b @ _model)
    prediction = max(0, min(100, prediction))

    return round(prediction, 2)