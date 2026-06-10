from flask import Blueprint, request, jsonify
from backend.db_connection import get_db


lsns_bp = Blueprint("lsns", __name__)

# ── Lessons ───────────────────────────────────────────────────────────────────

@lsns_bp.route("/lessons", methods=["GET"])
def get_lessons():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons")
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)


@lsns_bp.route("/lessons/pending", methods=["GET"])
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


@lsns_bp.route("/lessons/<int:lessonID>", methods=["GET"])
def get_lesson(lessonID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons WHERE lessonID = %s", (lessonID,))
    lesson = cursor.fetchone()
    cursor.close()

    if not lesson:
        return jsonify({"error": "lesson not found"}), 404

    return jsonify(lesson)


@lsns_bp.route("/lessons", methods=["POST"])
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


@lsns_bp.route("/lessons/<int:lessonID>", methods=["PUT"])
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


@lsns_bp.route("/lessons/<int:lessonID>", methods=["DELETE"])
def delete_lesson(lessonID):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Lessons WHERE lessonID = %s", (lessonID,))
    db.commit()
    cursor.close()
    return jsonify({"message": "lesson deleted"})


@lsns_bp.route("/lessons/<int:lessonID>/approve", methods=["PUT"])
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


@lsns_bp.route("/lessons/<int:lessonID>/reject", methods=["PUT"])
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


@lsns_bp.route("/lessons/class/<int:classID>", methods=["GET"])
def get_lessons_by_class(classID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Lessons WHERE classID = %s", (classID,))
    lessons = cursor.fetchall()
    cursor.close()
    return jsonify(lessons)
