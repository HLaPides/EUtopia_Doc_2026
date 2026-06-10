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
    cursor.execute("SELECT * FROM Roles")
    roles = cursor.fetchall()
    cursor.close()
    return jsonify(roles)


@api_bp.route("/users/<int:userID>/roles", methods=["GET"])
def get_user_roles(userID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT Roles.roleID, Roles.roleName
        FROM UserRole
        JOIN Roles ON UserRole.roleID = Roles.roleID
        WHERE UserRole.userID = %s
        """,
        (userID,)
    )
    roles = cursor.fetchall()
    cursor.close()
    return jsonify(roles)


@api_bp.route("/users/by-role/<roleName>", methods=["GET"])
def get_users_by_role(roleName):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT U.userID, U.firstName, U.lastName, U.email
        FROM Users U
            JOIN UserRole UR ON U.userID = UR.userID
            JOIN Roles R ON UR.roleID = R.roleID
        WHERE R.roleName = %s""", (roleName,))
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)


# ── Lessons ───────────────────────────────────────────────────────────────────

@api_bp.route("/lessons", methods=["GET"])
def get_lessons():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons")
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)


@api_bp.route("/lessons/pending", methods=["GET"])
def get_pending_lessons():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT L.lessonID, L.teacherID, L.topicName, L.classID,
               CONCAT(U.firstName, ' ', U.lastName) AS teacherName,
               L.title, L.content, L.difficultyLevel, L.approvalStatus, L.createdAt
        FROM Lessons L LEFT JOIN Users U ON L.teacherID = U.userID
        WHERE L.approvalStatus = 'Pending'
    """)
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


@api_bp.route("/lessons/<int:lessonID>/approve", methods=["PUT"])
def approve_lesson(lessonID):
    data = request.get_json()
    officialID = data["officialID"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE Lessons
        SET approvalStatus = 'Approved',
            approvedBy = %s,
            updatedBy = %s
        WHERE lessonID = %s
        """,
        (officialID, officialID, lessonID)
    )
    db.commit()
    cursor.close()
    return jsonify({"message": "lesson approved"})


@api_bp.route("/lessons/<int:lessonID>/reject", methods=["PUT"])
def reject_lesson(lessonID):
    data = request.get_json()
    officialID = data["officialID"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE Lessons
        SET approvalStatus = 'Rejected',
            approvedBy = %s,
            updatedBy = %s
        WHERE lessonID = %s
        """,
        (officialID, officialID, lessonID)
    )
    db.commit()
    cursor.close()
    return jsonify({"message": "lesson rejected"})


@api_bp.route("/lessons/class/<int:classID>", methods=["GET"])
def get_lessons_by_class(classID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons WHERE classID = %s", (classID,))
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)


# ── Assessments & Questions ───────────────────────────────────────────────────

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


# ── Progress & Simulations ────────────────────────────────────────────────────

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


# ── ML ────────────────────────────────────────────────────────────────────────
@api_bp.route("/turnout-dataset", methods=["GET"])
def get_turnout_dataset():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM eu_turnout_dataset ORDER BY country, year")
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)

@api_bp.route("/simulations", methods=["POST"])
def create_simulation():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO Simulation
        (studentID, countryName, population, unemploymentRate, compulsoryVoting,
        medianAge, region, nationalTurnout, predictedTurnout, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("studentID"),
            data.get("countryName"),
            data.get("population"),
            data.get("unemploymentRate"),
            data.get("compulsoryVoting"),
            data.get("medianAge"),
            data.get("region"),
            data.get("nationalTurnout"),
            data.get("predictedTurnout"),
            data.get("studentID"),
            data.get("studentID"),
        )
    )

    db.commit()
    cursor.close()
    return jsonify({"message": "simulation saved"}), 201


@api_bp.route("/ml/turnout-prediction", methods=["POST"])
def turnout_prediction():
    data = request.get_json()
    result = predict_turnout(data)
    return jsonify(result)


# ── Classes ───────────────────────────────────────────────────────────────────

@api_bp.route("/responses", methods=["POST"])
def submit_response():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO Response (studentID, questionID, input, score, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            data.get("studentID"),
            data.get("questionID"),
            data.get("input"),
            data.get("score"),
            data.get("studentID"),
            data.get("studentID"),
        )
    )

    db.commit()
    cursor.close()
    return jsonify({"message": "response submitted"}), 201

@api_bp.route("/classes", methods=["GET"])
def get_classes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class")
    classes = cursor.fetchall()
    cursor.close()
    return jsonify(classes)


@api_bp.route("/classes/<int:classID>", methods=["GET"])
def get_class(classID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class WHERE classID = %s", (classID,))
    cls = cursor.fetchone()
    cursor.close()

    if not cls:
        return jsonify({"error": "class not found"}), 404

    return jsonify(cls)


@api_bp.route("/classes/teacher/<int:teacherID>", methods=["GET"])
def get_teacher_classes(teacherID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class WHERE teacherID = %s", (teacherID,))
    classes = cursor.fetchall()
    cursor.close()
    return jsonify(classes)


@api_bp.route("/classes/<int:classID>/students", methods=["GET"])
def get_class_students(classID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.userID, u.firstName, u.lastName, u.email
        FROM StudentProfile sp
        JOIN Users u ON sp.studentID = u.userID
        WHERE sp.classID = %s
    """, (classID,))
    students = cursor.fetchall()
    cursor.close()
    return jsonify(students)


@api_bp.route("/classes", methods=["POST"])
def create_class():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO Class (teacherID, className, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["teacherID"],
            data["className"],
            data.get("createdBy"),
            data.get("updatedBy"),
        )
    )
    db.commit()
    classID = cursor.lastrowid
    cursor.close()
    return jsonify({"message": "class created", "classID": classID}), 201


@api_bp.route("/classes/<int:classID>", methods=["PUT"])
def update_class(classID):
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        UPDATE Class
        SET className = %s,
            updatedBy = %s
        WHERE classID = %s
        """,
        (
            data["className"],
            data.get("updatedBy"),
            classID,
        )
    )
    db.commit()
    cursor.close()
    return jsonify({"message": "class updated"})


@api_bp.route("/classes/<int:classID>", methods=["DELETE"])
def delete_class(classID):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Class WHERE classID = %s", (classID,))
    db.commit()
    cursor.close()
    return jsonify({"message": "class deleted"})


# ── Students ──────────────────────────────────────────────────────────────────

@api_bp.route("/students/<int:studentID>/profile", methods=["GET"])
def get_student_profile(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StudentProfile WHERE studentID = %s", (studentID,))
    profile = cursor.fetchone()
    cursor.close()

    if not profile:
        return jsonify({"error": "profile not found"}), 404

    return jsonify(profile)


# ── Surveys ───────────────────────────────────────────────────────────────────

@api_bp.route("/surveys", methods=["POST"])
def submit_survey():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        """
        INSERT INTO DiagnosticSurvey
        (studentID, age, educationLevel, gender, politicalInterest,
         trustNationalParliament, trustPoliticians, satisfactionDemocracy,
         predictedTrust, createdBy, updatedBy)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            data["studentID"],
            data.get("age"),
            data.get("educationLevel"),
            data.get("gender"),
            data.get("politicalInterest"),
            data.get("trustNationalParliament"),
            data.get("trustPoliticians"),
            data.get("satisfactionDemocracy"),
            data.get("predictedTrust"),
            data["studentID"],
            data["studentID"],
        )
    )
    db.commit()
    cursor.close()
    return jsonify({"message": "survey submitted"}), 201


@api_bp.route("/surveys", methods=["GET"])
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