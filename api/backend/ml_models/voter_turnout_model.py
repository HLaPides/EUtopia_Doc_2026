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

Model is fit on the full dataset when train() is called. LOO-CV is used as the
primary performance metric given the relatively small dataset (184 observations).

Final performance: LOO-CV R2=0.7928, LOO-CV MSE=77.61

ROUTES NEEDED (to be implemented):
  POST   /simulations/train       -> calls train(), admin only
  GET    /simulations/test        -> calls test(), admin only
  GET    /simulations/<id>/predict -> calls predict() with features from simulation row
"""
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
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


# ============================================================
# PRIVATE HELPERS
# These are internal functions that should never be called
# directly by routes. They are only used by the public
# functions below.
# ============================================================

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
# These are the functions that should be called by routes.
# ============================================================

# ROUTE: POST /simulations/train  (admin only)
# Accepts an optional file path in the request body to retrain on new data.
# Returns training metrics so the admin can verify the model improved.
def train(data_path: str = "datasets/eu_turnout_clean.csv") -> dict:
    """
    Retrains the OLS model on the full dataset and writes the new
    coefficients and scaler parameters to the DB. Can be triggered
    from an admin route to retrain the model without redeploying.

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
    df = pd.read_csv(data_path)
    df["median_age_sq"]        = df["median_age"] ** 2
    df["national_turnout_sq"]  = df["national_turnout"] ** 2
    df["compulsory_x_western"] = df["compulsory_voting"] * df["region_western"]

    X = df[FEATURES].values
    y = df[TARGET].values

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    X_b = np.column_stack([np.ones(len(X_scaled)), X_scaled])
    b   = np.linalg.inv(X_b.T @ X_b) @ (X_b.T @ y)

    y_hat = X_b @ b
    mse   = ((y_hat - y) ** 2).mean()
    r2    = 1 - mse / y.var()

    means_list = scaler.mean_.tolist()
    stds_list  = scaler.scale_.tolist()
    beta_list  = b.tolist()

    current_app.logger.info(f'voter_turnout train() R2={r2:.4f} MSE={mse:.4f}')
    current_app.logger.info(f'beta_vals: {beta_list}')
    current_app.logger.info(f'means: {means_list}')
    current_app.logger.info(f'stds:  {stds_list}')

    # TODO: uncomment once voter_turnout_params and voter_turnout_scaler tables exist
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
    df = pd.read_csv("datasets/eu_turnout_clean.csv")
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

    current_app.logger.info(f'voter_turnout test() LOO-CV R2={r2_loo:.4f} MSE={mse_loo:.4f}')

    return {
        'loo_cv_r2':  round(r2_loo, 4),
        'loo_cv_mse': round(mse_loo, 4),
        'n':          len(y),
    }


# ROUTE: GET /simulations/<simulation_id>/predict
# Route should read the simulation row from the DB by simulation_id,
# extract the feature values, and pass them to this function.
# Writes the result back to the predictedTurnout column in the Simulation table.
# Example call:
#   from backend.ml_models import voter_turnout_model
#   prediction = voter_turnout_model.predict(
#       compulsory_voting=1,
#       median_age=38.5,
#       national_turnout=72.3,
#       unemployment_rate=5.2,
#       population=11000000,
#       region_northern=0,
#       region_southern=0,
#       region_western=1,
#   )
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

    Args:
        compulsory_voting : 1 if compulsory voting is enforced, 0 otherwise
        median_age        : median age of the population
        national_turnout  : national election turnout (%)
        unemployment_rate : unemployment rate (%)
        population        : country population
        region_northern   : 1 if Northern Europe, 0 otherwise
        region_southern   : 1 if Southern Europe, 0 otherwise
        region_western    : 1 if Western Europe, 0 otherwise
                            (Eastern Europe is the reference category —
                            all three region flags = 0)

    Returns:
        float: predicted voter turnout (%)

    Raises:
        TypeError:  if any argument is the wrong type
        ValueError: if no params exist in the DB yet
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
    current_app.logger.info(
        f'voter_turnout_model.predict() -> {prediction:.2f}%'
    )
    return prediction