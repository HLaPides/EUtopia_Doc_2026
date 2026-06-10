from flask import Blueprint, request, jsonify
from backend.db_connection import get_db


asmts_bp = Blueprint("asmts", __name__)

# ── Assessments & Questions ───────────────────────────────────────────────────

@asmts_bp.route("/assessments", methods=["GET"])
def get_assessments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Assessment")
    assessments = cursor.fetchall()
    cursor.close()
    return jsonify(assessments)


@asmts_bp.route("/questions/<int:assessmentID>", methods=["GET"])
def get_questions_for_assessment(assessmentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Question WHERE assessmentID = %s", (assessmentID,))
    questions = cursor.fetchall()
    cursor.close()
    return jsonify(questions)