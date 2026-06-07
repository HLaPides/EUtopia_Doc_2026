"""
eu_trust_model.py — EU Institutional Trust Prediction

Logistic regression model predicting whether an individual trusts the EU
based on their political attitudes and institutional trust levels.
Trained on the Autumn 2024 Eurobarometer wave (n=23,343).

Features:
  - education             : education level (1-8 scale)
  - trust_parliament      : trust in national parliament (1=trust, 2=distrust)
  - trust_politicians     : trust in politicians (1=trust, 2=distrust)
  - satisfaction_democracy: satisfaction with democracy (1=very satisfied, 4=not at all)
  - left_right            : left-right political self-placement (1-10 scale)

Target:
  - trust_eu : 1 = trusts EU, 0 = does not trust EU
               (don't know responses filtered out at training time)

Final performance: Test Accuracy=0.732, Train Accuracy=0.729

"""
import os
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from flask import current_app
from backend.db_connection import get_db

FEATURES = [
    "education",
    "trust_parliament",
    "trust_politicians",
    "satisfaction_democracy",
    "left_right",
]
TARGET = "trust_eu"


# ============================================================
# PRIVATE HELPERS
# ============================================================

def _get_csv_path() -> str:
    """
    Resolves the dataset path relative to this file's location.
    Used by train() and test() only — predict() reads from the DB.

    NOTE: eurobarometer_cleaned.csv must exist at this path. If the file
    is moved or renamed, train() and test() will both fail.
    """
    return os.path.join(os.path.dirname(__file__), "eurobarometer_cleaned.csv")


def _get_params() -> tuple[np.ndarray, float]:
    """
    Fetches the most recent model parameters from eu_trust_params.

    Returns:
        tuple: (coef, intercept) where coef is a 1-D array of length 5
               and intercept is a float

    Raises:
        ValueError: if no parameters exist in the database yet.
    """
    with get_db().cursor(dictionary=True) as cursor:
        cursor.execute(
            'SELECT coef_vals, intercept FROM eu_trust_params '
            'ORDER BY sequence_number DESC LIMIT 1'
        )
        row = cursor.fetchone()

    if row is None:
        raise ValueError("No eu_trust_params found in the database.")

    coef      = np.array(json.loads(row['coef_vals']))
    intercept = float(row['intercept'])
    current_app.logger.info(f'eu_trust_model params loaded: coef={coef}')
    return coef, intercept

# ROUTE: POST /trust/train  (EU official only)
# Accepts an optional file upload path to retrain on new data.
# Returns training metrics so the EU official can verify the model.
def train(data_path: str = None) -> dict:
    """
    Retrains the logistic regression model on the full dataset and writes
    the new coefficients and intercept to the DB atomically.
    If the DB write fails, it is rolled back.

    Args:
        data_path: path to the training CSV. Defaults to the standard
                   dataset location. Pass a different path to retrain
                   on updated data — the route should accept a file
                   upload, save it to /tmp, and pass the path here.

    Returns:
        dict: {
            'train_accuracy': float,
            'test_accuracy':  float,
            'n':              int
        }

    Raises:
        Exception: if DB write fails, rolls back and re-raises.
    """
    if data_path is None:
        data_path = _get_csv_path()

    df = pd.read_csv(data_path).dropna()

    # filter out don't know responses for trust_eu (coded as 3)
    df = df[df[TARGET].isin([0, 1])]

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    train_acc = model.score(X_train, y_train)
    test_acc  = model.score(X_test, y_test)

    coef_list      = model.coef_[0].tolist()
    intercept_val  = float(model.intercept_[0])

    current_app.logger.info(
        f'eu_trust train() train_acc={train_acc:.4f} test_acc={test_acc:.4f}'
    )

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute(
                'SELECT COALESCE(MAX(sequence_number), 0) + 1 FROM eu_trust_params'
            )
            next_seq = cursor.fetchone()[0]
            cursor.execute(
                'INSERT INTO eu_trust_params (sequence_number, coef_vals, intercept) '
                'VALUES (%s, %s, %s)',
                (next_seq, json.dumps(coef_list), intercept_val)
            )
        db.commit()
    except Exception as e:
        db.rollback()
        current_app.logger.error(f'eu_trust train() DB write failed: {e}')
        raise

    return {
        'train_accuracy': round(train_acc, 4),
        'test_accuracy':  round(test_acc, 4),
        'n':              len(y),
    }


# ROUTE: GET /trust/test  (EU official only)
# No inputs needed. Returns accuracy metrics on a fresh train/test split.
def test() -> dict:
    """
    Evaluates the model on a fresh 80/20 train/test split and returns
    accuracy metrics.

    Returns:
        dict: {
            'train_accuracy': float,
            'test_accuracy':  float,
            'n':              int
        }
    """
    df = pd.read_csv(_get_csv_path()).dropna()
    df = df[df[TARGET].isin([0, 1])]

    X = df[FEATURES].values
    y = df[TARGET].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    return {
        'train_accuracy': round(model.score(X_train, y_train), 4),
        'test_accuracy':  round(model.score(X_test, y_test), 4),
        'n':              len(y),
    }


# ROUTE: POST /ml/trust-prediction
# Called by the trust_prediction route.
# Accepts a JSON dict of raw feature values, returns predicted trust
# as both a binary label and a probability.
def predict(
    education: float,
    trust_parliament: int,
    trust_politicians: int,
    satisfaction_democracy: int,
    left_right: float,
) -> dict:
    """
    Returns a trust prediction given the input features.
    Applies the logistic function manually using coefficients from the DB.

    Args:
        education              : education level (1-8 scale)
        trust_parliament       : 1=trusts parliament, 2=does not trust
        trust_politicians      : 1=trusts politicians, 2=does not trust
        satisfaction_democracy : 1=very satisfied, 4=not at all satisfied
        left_right             : left-right self-placement (1-10 scale)

    Returns:
        dict: {
            'prediction':   int,   # 1 = trusts EU, 0 = does not trust
            'probability':  float  # probability of trusting EU (0-1)
        }
    """
    coef, intercept = _get_params()

    x = np.array([
        education,
        trust_parliament,
        trust_politicians,
        satisfaction_democracy,
        left_right,
    ])

    z           = intercept + np.dot(coef, x)
    probability = float(1 / (1 + np.exp(-z)))
    prediction  = 1 if probability >= 0.5 else 0

    current_app.logger.info(
        f'eu_trust_model.predict() -> {prediction} (p={probability:.3f})'
    )

    return {
        'prediction':  prediction,
        'probability': round(probability, 4),
    }


def predict_trust(data: dict) -> dict:
    """
    Dict-based wrapper around predict() for use by the Flask route.
    Accepts a JSON body dict, extracts and validates feature values,
    and returns prediction and probability.

    Args:
        data: dict with keys:
            education, trust_parliament, trust_politicians,
            satisfaction_democracy, left_right

    Returns:
        dict: {
            'prediction':  int,   # 1 = trusts EU, 0 = does not trust
            'probability': float  # probability of trusting EU (0-1)
        }
    """
    return predict(
        education              = float(data.get("education")),
        trust_parliament       = int(data.get("trust_parliament")),
        trust_politicians      = int(data.get("trust_politicians")),
        satisfaction_democracy = int(data.get("satisfaction_democracy")),
        left_right             = float(data.get("left_right")),
    )