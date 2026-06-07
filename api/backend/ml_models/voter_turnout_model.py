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

Model parameters and scaler values are stored in voter_turnout_params and
voter_turnout_scaler tables in the DB. train() reads the CSV, fits the model,
and writes the new parameters to the DB. predict() reads from the DB.

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
from sklearn.neighbors import NearestNeighbors
from flask import current_app
from backend.db_connection import get_db

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
_knn    = None
_df     = None


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _get_csv_path() -> str:
    """
    Resolves the dataset path relative to this file's location.
    Used by train() and test() only — predict() reads from the DB.

    NOTE: eu_turnout_clean.csv must exist at this path. If the file
    is moved or renamed, train() and test() will both fail.
    """
    return os.path.join(os.path.dirname(__file__), "eu_turnout_clean.csv")


def _get_params() -> np.ndarray:
    """
    Fetches the most recent coefficient vector from voter_turnout_params.

    Returns:
        np.ndarray: 1-D array of length 12 [intercept, b1, ..., b11]

    Raises:
        ValueError: if no parameters exist in the database yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT beta_vals FROM voter_turnout_params '
            'ORDER BY sequence_number DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No voter_turnout_params found in the database.")

    params = np.array(json.loads(row['beta_vals']))
    current_app.logger.info(f'voter_turnout_model params loaded: {params}')
    return params


def _get_scaler_params() -> tuple[np.ndarray, np.ndarray]:
    """
    Fetches the most recent scaler parameters from voter_turnout_scaler.
    These are the mean and std of each feature at training time, needed
    to apply the same standardization to user inputs at prediction time.

    Returns:
        tuple: (means, stds) as np.ndarrays of length 11 (one per feature)

    Raises:
        ValueError: if no scaler parameters exist in the database yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT feature_means, feature_stds FROM voter_turnout_scaler '
            'ORDER BY sequence_number DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No voter_turnout_scaler params found in the database.")

    means = np.array(json.loads(row['feature_means']))
    stds  = np.array(json.loads(row['feature_stds']))
    return means, stds


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


# ============================================================
# PUBLIC FUNCTIONS
# ============================================================

# ROUTE: POST /simulations/train  (admin only)
# Accepts an optional file upload path to retrain on new data.
# Returns training metrics so the admin can verify the model improved.
def train(data_path: str = None) -> dict:
    """
    Retrains the OLS model on the full dataset and writes the new
    coefficients and scaler parameters to the DB atomically.
    If either DB write fails, both are rolled back.

    Args:
        data_path: path to the training CSV. Defaults to the standard
                   dataset location. Pass a different path to retrain
                   on updated data — the route should accept a file
                   upload, save it to /tmp, and pass the path here.

    Returns:
        dict: {
            'r2_train': float,
            'mse_train': float,
            'n': int
        }
    """
    global _model, _scaler, _knn, _df

    #Raises:
    #Exception: if DB writes fail, rolls back and re-raises.

    if data_path is None:
        data_path = _get_csv_path()

    df = pd.read_csv(data_path)
    df["median_age_sq"]        = df["median_age"] ** 2
    df["national_turnout_sq"]  = df["national_turnout"] ** 2
    df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

    X = df[FEATURES].values
    y = df[TARGET].values

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    _scaler  = scaler

    X_b = np.column_stack([np.ones(len(X_scaled)), X_scaled])
    b   = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)

    # fit KNN on the full scaled dataset
    _knn = NearestNeighbors(n_neighbors=1, metric='euclidean')
    _knn.fit(X_scaled)
    _df = df[['country', 'year', 'voter_turnout']].reset_index(drop=True)

    y_hat = X_b @ b
    
    mse   = ((y_hat - y) ** 2).mean()
    r2    = 1 - mse / y.var()

    means_list = scaler.mean_.tolist()
    stds_list  = scaler.scale_.tolist()
    beta_list  = b.tolist()

    current_app.logger.info(f'voter_turnout train() R2={r2:.4f} MSE={mse:.4f}')

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM voter_turnout_params'
            )
            next_seq = cursor.fetchone()[0]
            cursor.execute(
                'INSERT INTO voter_turnout_params (sequence_number, beta_vals) VALUES (%s, %s)',
                (next_seq, json.dumps(beta_list))
            )
            cursor.execute(
                'INSERT INTO voter_turnout_scaler (sequence_number, feature_means, feature_stds) '
                'VALUES (%s, %s, %s)',
                (next_seq, json.dumps(means_list), json.dumps(stds_list))
            )
        db.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(f'voter_turnout train() DB write failed: {e}')
        raise

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
    Reads model parameters and scaler values from the DB.

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
    params      = _get_params()
    means, stds = _get_scaler_params()

    x_raw     = _engineer_features(
        compulsory_voting, median_age, national_turnout,
        unemployment_rate, population, region_northern,
        region_southern, region_western
    )
    x_scaled  = (x_raw - means) / stds
    input_vec = np.array([1.0, *x_scaled])

    prediction = float(params.T @ input_vec)
    current_app.logger.info(f'voter_turnout_model.predict() -> {prediction:.2f}%')
    return prediction

def find_similar_country(
    compulsory_voting: int,
    median_age: float,
    national_turnout: float,
    unemployment_rate: float,
    population: float,
    region_northern: int,
    region_southern: int,
    region_western: int,
) -> dict:
    global _knn, _scaler, _df

    if _knn is None or _scaler is None:
        train()

    x_raw    = _engineer_features(
        compulsory_voting, median_age, national_turnout,
        unemployment_rate, population, region_northern,
        region_southern, region_western
    )
    x_scaled = _scaler.transform(x_raw.reshape(1, -1))

    distances, indices = _knn.kneighbors(x_scaled)
    match = _df.iloc[indices[0][0]]

    return {
        'country': match['country'],
        'year': int(match['year']),
        'voter_turnout': round(float(match['voter_turnout']), 1)
    }

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

    similar = find_similar_country(
        compulsory_voting = int(data.get("compulsory_voting", 0)),
        median_age        = float(data.get("median_age")),
        national_turnout  = float(data.get("national_turnout")),
        unemployment_rate = float(data.get("unemployment_rate")),
        population        = float(data.get("population")),
        region_northern   = int(data.get("region_northern", 0)),
        region_southern   = int(data.get("region_southern", 0)),
        region_western    = int(data.get("region_western", 0)),
    )

    return {
        'predicted_turnout': round(max(0.0, min(100.0, prediction)), 2),
        'similar_country': f"{similar['country']} ({similar['year']})",
        'similar_country_turnout': similar['voter_turnout']
    }