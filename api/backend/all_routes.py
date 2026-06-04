from flask import Blueprint, request, jsonify
from backend.db_connection import get_db
from backend.ml_models.voter_turnout_model import predict_turnout


api_bp = Blueprint("api", __name__)


@api_bp.route("/users", methods=["GET"])
def get_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)


@api_bp.route("/users/<int:userID>", methods=["GET"])
def get_user(userID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE userID = %s", (userID,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify(user)


@api_bp.route("/roles", methods=["GET"])
def get_roles():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Role")
    roles = cursor.fetchall()
    cursor.close()
    return jsonify(roles)


@api_bp.route("/users/<int:userID>/roles", methods=["GET"])
def get_user_roles(userID):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT Role.roleID, Role.roleName
        FROM UserRole
        JOIN Role ON UserRole.roleID = Role.roleID
        WHERE UserRole.userID = %s
        """,
        (userID,)
    )

    roles = cursor.fetchall()
    cursor.close()
    return jsonify(roles)


@api_bp.route("/lessons", methods=["GET"])
def get_lessons():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons")
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)


@api_bp.route("/lessons/<int:lessonID>", methods=["GET"])
def get_lesson(lessonID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons WHERE lessonID = %s", (lessonID,))
    lesson = cursor.fetchone()
    cursor.close()

    if not lesson:
        return jsonify({"error": "lesson not found"}), 404

    return jsonify(lesson)


@api_bp.route("/lessons", methods=["POST"])
def create_lesson():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO Lessons
        (classID, teacherID, approvedBy, title, topicName, content, difficultyLevel, approvalStatus, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("classID"),
            data["teacherID"],
            data.get("approvedBy"),
            data["title"],
            data.get("topicName"),
            data["content"],
            data.get("difficultyLevel"),
            data.get("approvalStatus", "Pending"),
            data.get("createdBy"),
            data.get("updatedBy"),
        )
    )

    db.commit()
    lessonID = cursor.lastrowid
    cursor.close()

    return jsonify({"message": "lesson created", "lessonID": lessonID}), 201


@api_bp.route("/lessons/<int:lessonID>", methods=["PUT"])
def update_lesson(lessonID):
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        UPDATE Lessons
        SET title = %s,
            topicName = %s,
            content = %s,
            difficultyLevel = %s,
            approvalStatus = %s,
            updatedBy = %s
        WHERE lessonID = %s
        """,
        (
            data["title"],
            data.get("topicName"),
            data["content"],
            data.get("difficultyLevel"),
            data.get("approvalStatus"),
            data.get("updatedBy"),
            lessonID,
        )
    )

    db.commit()
    cursor.close()

    return jsonify({"message": "lesson updated"})


@api_bp.route("/lessons/<int:lessonID>", methods=["DELETE"])
def delete_lesson(lessonID):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Lessons WHERE lessonID = %s", (lessonID,))
    db.commit()
    cursor.close()

    return jsonify({"message": "lesson deleted"})


@api_bp.route("/assessments", methods=["GET"])
def get_assessments():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Assessment")
    assessments = cursor.fetchall()
    cursor.close()
    return jsonify(assessments)


@api_bp.route("/questions/<int:assessmentID>", methods=["GET"])
def get_questions_for_assessment(assessmentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Question WHERE assessmentID = %s", (assessmentID,))
    questions = cursor.fetchall()
    cursor.close()
    return jsonify(questions)


@api_bp.route("/progress/<int:studentID>", methods=["GET"])
def get_student_progress(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StudentProgress WHERE studentID = %s", (studentID,))
    progress = cursor.fetchall()
    cursor.close()
    return jsonify(progress)


@api_bp.route("/simulations/<int:studentID>", methods=["GET"])
def get_student_simulations(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Simulation WHERE studentID = %s", (studentID,))
    simulations = cursor.fetchall()
    cursor.close()
    return jsonify(simulations)


@api_bp.route("/ml/turnout-prediction", methods=["POST"])
def turnout_prediction():
    data = request.get_json()
    prediction = predict_turnout(data)

    return jsonify({
        "predictedTurnout": prediction,
        "inputs": data
    })