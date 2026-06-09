from flask import Blueprint, jsonify, current_app
from backend.ml_models.voter_turnout_model import train as vt_train, test as vt_test, FEATURES as vt_features
from backend.ml_models.eu_trust_model import train as trust_train, test as trust_test, FEATURES as trust_features

ml_bp = Blueprint("ml", __name__)

#Currently contains test/train features that should only be accessible via eu official


# ── Voter Turnout Model ───────────────────────────────────────────────────────

@ml_bp.route("/ml/voter-turnout/train", methods=["POST"])
def train_voter_turnout():
    current_app.logger.info("POST /ml/voter-turnout/train")
    try:
        result = vt_train()
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"voter turnout train error: {e}")
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/ml/voter-turnout/test", methods=["GET"])
def test_voter_turnout():
    current_app.logger.info("GET /ml/voter-turnout/test")
    try:
        result = vt_test()
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"voter turnout test error: {e}")
        return jsonify({"error": str(e)}), 500


# ── EU Trust Model ────────────────────────────────────────────────────────────

@ml_bp.route("/ml/eu-trust/train", methods=["POST"])
def train_eu_trust():
    current_app.logger.info("POST /ml/eu-trust/train")
    try:
        result = trust_train()
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"eu trust train error: {e}")
        return jsonify({"error": str(e)}), 500


@ml_bp.route("/ml/eu-trust/test", methods=["GET"])
def test_eu_trust():
    current_app.logger.info("GET /ml/eu-trust/test")
    try:
        result = trust_test()
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"eu trust test error: {e}")
        return jsonify({"error": str(e)}), 500


# ── Features ──────────────────────────────────────────────────────────────────

@ml_bp.route("/ml/voter-turnout/features", methods=["GET"])
def get_voter_turnout_features():
    current_app.logger.info("GET /ml/voter-turnout/features")
    return jsonify({"features": vt_features}), 200


@ml_bp.route("/ml/eu-trust/features", methods=["GET"])
def get_eu_trust_features():
    current_app.logger.info("GET /ml/eu-trust/features")
    return jsonify({"features": trust_features}), 200