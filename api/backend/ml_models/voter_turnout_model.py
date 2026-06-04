"""
voter_turnout_model.py — EU Parliamentary Election Voter Turnout Prediction

OLS linear regression model predicting EU parliamentary election voter turnout
across 27 EU member states from 1979-2024 (184 observations).

Features:
  - compulsory_voting     : binary, whether voting is legally required
  - median_age            : median age of the population
  - median_age_sq         : median age squared. relationship isn't linear,
                            its closer to a parabola than a line so we squared it
  - national_turnout      : national election turnout (%)
  - national_turnout_sq   : national election turnout squared, same reasoning
                            as median_age_sq
  - unemployment_rate     : unemployment rate (%)
  - population            : country population
  - compulsory_x_western  : interaction between compulsory voting and Western region.
                            compulsory voting is only meaningfully enforced in Western
                            Europe (Belgium and Luxembourg); Greece has compulsory
                            voting on paper but doesn't enforce it
  - region_northern/
    southern/western      : region binary columns with Eastern Europe as the reference
                            category. regional effects capture structural differences
                            in EU engagement not explained by the other features.
                            Eastern Europe averages around 20pp lower turnout than Western

Currently uses in-memory model trained on startup. DB storage is stubbed out
and can be enabled once voter_turnout_params and voter_turnout_scaler tables
exist in the schema (see commented out sections in train() and the _get_params
/ _get_scaler_params helpers).

Final performance: LOO-CV R2=0.7928, LOO-CV MSE=77.61

ROUTES NEEDED (to be implemented in simulations_routes.py):
  POST   /simulations/train        -> calls train(), admin only
  GET    /simulations/test         -> calls test(), admin only
  POST   /ml/turnout-prediction    -> calls predict_turnout() with JSON body
"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from flask import current_app

# TODO: uncomment when DB tables exist
# from backend.db_connection import get_db

FEATURES = [
    "compulsory_voting",
    "median_age",
    "median_age_sq",
    "national_turnout",
    "national_turnout_sq",
    "unemployment_rate",
    "population",
    "compulsory_x_western",
    "region_northern",
    "region_southern",
    "region_western",
]
TARGET = "voter_turnout"

# in-memory model state — populated by train() on first predict call
_model  = None
_scaler = None


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _get_csv_path() -> str:
    """
    Resolves the dataset path relative to this file's location.

    TEMPORARY: eu_turnout_clean.csv is copied into api/backend/ml_models/
    so the API container can access it at runtime. This is only needed
    because the DB tables do not exist yet. Once voter_turnout_params and
    voter_turnout_scaler are added to the schema and train() DB writes are
    uncommented, this function and the CSV copy can be removed entirely.
    """
    return os.path.join(os.path.dirname(__file__), "eu_turnout_clean.csv")


def _engineer_features(
    compulsory_voting: int,
    median_age: float,
    national_turnout: float,
    unemployment_rate: float,
    population: float,
    region_northern: int,
    region_southern: int,
    region_western: int,
) -> np.ndarray:
    """
    Builds the full 11-feature vector from raw inputs, applying the same
    transformations used at training time (squared terms, interaction term).

    Returns:
        np.ndarray: 1-D array of length 11 in the same order as FEATURES
    """
    compulsory_x_western = compulsory_voting * region_western
    median_age_sq        = median_age ** 2
    national_turnout_sq  = national_turnout ** 2

    return np.array([
        compulsory_voting,
        median_age,
        median_age_sq,
        national_turnout,
        national_turnout_sq,
        unemployment_rate,
        population,
        compulsory_x_western,
        region_northern,
        region_southern,
        region_western,
    ])

# TODO: when DB tables exist, replace in-memory state with these helpers
# def _get_params() -> np.ndarray:
#     with get_db().cursor(dictionary=True) as cursor:
#         cursor.execute(
#             'SELECT beta_vals FROM voter_turnout_params '
#             'ORDER BY sequence_number DESC LIMIT 1'
#         )
#         row = cursor.fetchone()
#     if row is None:
#         raise ValueError("No voter_turnout_params found in the database.")
#     return np.array(json.loads(row['beta_vals']))
#
# def _get_scaler_params() -> tuple[np.ndarray, np.ndarray]:
#     with get_db().cursor(dictionary=True) as cursor:
#         cursor.execute(
#             'SELECT feature_means, feature_stds FROM voter_turnout_scaler '
#             'ORDER BY sequence_number DESC LIMIT 1'
#         )
#         row = cursor.fetchone()
#     if row is None:
#         raise ValueError("No voter_turnout_scaler params found in the database.")
#     means = np.array(json.loads(row['feature_means']))
#     stds  = np.array(json.loads(row['feature_stds']))
#     return means, stds


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

# ROUTE: POST /simulations/train  (admin only)
# Accepts an optional file path in the request body to retrain on new data.
# Returns training metrics so the admin can verify the model improved.
def train(data_path: str = None) -> dict:
    """
    Trains the OLS model on the full dataset and stores it in memory.
    Call this to retrain on new data without redeploying.

    Args:
        data_path: path to the training CSV. Defaults to the standard
                   dataset location. Pass a different path to retrain
                   on updated data.

    Returns:
        dict: {
            'r2_train': float,
            'mse_train': float,
            'n': int
        }
    """
    global _model, _scaler

    if data_path is None:
        data_path = _get_csv_path()

    df = pd.read_csv(data_path)
    df["median_age_sq"]        = df["median_age"] ** 2
    df["national_turnout_sq"]  = df["national_turnout"] ** 2
    df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

    X = df[FEATURES].values
    y = df[TARGET].values

    _scaler  = StandardScaler()
    X_scaled = _scaler.fit_transform(X)

    X_b    = np.column_stack([np.ones(len(X_scaled)), X_scaled])
    _model = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)

    y_hat = X_b @ _model
    mse   = ((y_hat - y) ** 2).mean()
    r2    = 1 - mse / y.var()

    # TODO: when DB tables exist, write _model and _scaler params to DB here
    # means_list = _scaler.mean_.tolist()
    # stds_list  = _scaler.scale_.tolist()
    # beta_list  = _model.tolist()
    # with get_db().cursor() as cursor:
    #     cursor.execute(
    #         'SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM voter_turnout_params'
    #     )
    #     next_seq = cursor.fetchone()[0]
    #     cursor.execute(
    #         'INSERT INTO voter_turnout_params (sequence_number, beta_vals) VALUES (%s, %s)',
    #         (next_seq, json.dumps(beta_list))
    #     )
    #     cursor.execute(
    #         'INSERT INTO voter_turnout_scaler (sequence_number, feature_means, feature_stds) '
    #         'VALUES (%s, %s, %s)',
    #         (next_seq, json.dumps(means_list), json.dumps(stds_list))
    #     )
    #     get_db().commit()

    return {
        'r2_train':  round(r2, 4),
        'mse_train': round(mse, 4),
        'n':         len(y),
    }


# ROUTE: GET /simulations/test  (admin only)
# No inputs needed. Returns LOO-CV metrics so the admin can verify
# model performance before deploying to students.
def test() -> dict:
    """
    Runs LOO-CV on the full dataset and returns performance metrics.
    LOO-CV is used because the dataset is relatively small (184 observations)
    so a single train/test split would be unreliable.

    Returns:
        dict: {
            'loo_cv_r2':  float,   # target: ~0.79
            'loo_cv_mse': float,   # target: ~77.61
            'n':          int
        }
    """
    df = pd.read_csv(_get_csv_path())
    df["median_age_sq"]        = df["median_age"] ** 2
    df["national_turnout_sq"]  = df["national_turnout"] ** 2
    df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

    X = df[FEATURES].values
    y = df[TARGET].values

    scaler_loo   = StandardScaler()
    X_loo_scaled = scaler_loo.fit_transform(X)

    y_loo = np.empty(len(y))
    for i in range(len(y)):
        X_train = np.concatenate([X_loo_scaled[:i], X_loo_scaled[i+1:]])
        y_train = np.concatenate([y[:i], y[i+1:]])
        X_b     = np.column_stack([np.ones(len(X_train)), X_train])
        b_loo   = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y_train)
        y_loo[i] = np.array([1.0, *X_loo_scaled[i]]) @ b_loo

    mse_loo = ((y_loo - y) ** 2).mean()
    r2_loo  = 1 - mse_loo / y.var()

    return {
        'loo_cv_r2':  round(r2_loo, 4),
        'loo_cv_mse': round(mse_loo, 4),
        'n':          len(y),
    }


# ROUTE: POST /ml/turnout-prediction
# Called by the turnout_prediction route in all_routes.py.
# Accepts a JSON dict of raw feature values, returns predicted turnout
# clamped to [0, 100].
def predict(
    compulsory_voting: int,
    median_age: float,
    national_turnout: float,
    unemployment_rate: float,
    population: float,
    region_northern: int,
    region_southern: int,
    region_western: int,
) -> float:
    """
    Returns a single voter turnout prediction given the input features.
    Trains the model in memory on first call if not already trained.

    Args:
        compulsory_voting : 1 if compulsory voting is enforced, 0 otherwise
        median_age        : median age of the population
        national_turnout  : national election turnout (%)
        unemployment_rate : unemployment rate (%)
        population        : country population
        region_northern   : 1 if Northern Europe, 0 otherwise
        region_southern   : 1 if Southern Europe, 0 otherwise
        region_western    : 1 if Western Europe, 0 otherwise
                            (Eastern Europe is the reference category,
                            all three region flags = 0)

    Returns:
        float: predicted voter turnout (%)
    """
    global _model, _scaler

    if _model is None or _scaler is None:
        train()

    x_raw     = _engineer_features(
        compulsory_voting, median_age, national_turnout,
        unemployment_rate, population, region_northern,
        region_southern, region_western
    )
    x_scaled  = _scaler.transform(x_raw.reshape(1, -1))
    input_vec = np.column_stack([np.ones(1), x_scaled])

    return float(input_vec @ _model)


def predict_turnout(data: dict) -> float:
    """
    Dict-based wrapper around predict() for use by the Flask route.
    Accepts a JSON body dict, extracts and validates feature values,
    and returns a predicted turnout percentage clamped to [0, 100].

    Args:
        data: dict with keys:
            compulsory_voting, median_age, national_turnout,
            unemployment_rate, population, region_northern,
            region_southern, region_western

    Returns:
        float: predicted voter turnout (%), clamped to [0, 100]
    """
    prediction = predict(
        compulsory_voting = int(data.get("compulsory_voting", 0)),
        median_age        = float(data.get("median_age")),
        national_turnout  = float(data.get("national_turnout")),
        unemployment_rate = float(data.get("unemployment_rate")),
        population        = float(data.get("population")),
        region_northern   = int(data.get("region_northern", 0)),
        region_southern   = int(data.get("region_southern", 0)),
        region_western    = int(data.get("region_western", 0)),
    )
    return round(max(0.0, min(100.0, prediction)), 2)