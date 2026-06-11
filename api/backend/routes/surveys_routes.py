from flask import Blueprint, request, jsonify
from backend.db_connection import get_db
from backend.ml_models.voter_turnout_model import predict_turnout


svys_bp = Blueprint("svys", __name__)

# ── Surveys ───────────────────────────────────────────────────────────────────
@svys_bp.route("/surveys", methods=["POST"])
def submit_survey():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO DiagnosticSurvey
        (studentID, educationLevel, politicalAffiliation, trustEuroParliament,
        trustPoliticians, satisfactionDemocracy, predictedTrust, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["studentID"],
            data.get("educationLevel"),
            str(data.get("leftRight")),
            data.get("trustEuroParliament"),
            data.get("trustPoliticians"),
            data.get("democracySatisfaction"),
            data.get("predictedTrust"),
            data["studentID"],
            data["studentID"],
        )
    )
    db.commit()
    cursor.close()
    return jsonify({"message": "survey submitted"}), 201


@svys_bp.route("/surveys", methods=["GET"])
def get_surveys():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ds.*, u.firstName, u.lastName
        FROM DiagnosticSurvey ds
        JOIN Users u ON ds.studentID = u.userID
        ORDER BY ds.createdAt DESC
    """)
    surveys = cursor.fetchall()
    cursor.close()
    return jsonify(surveys)