from flask import Blueprint, request, jsonify
from backend.db_connection import get_db


class_bp = Blueprint("class", __name__)


# ── Classes ───────────────────────────────────────────────────────────────────

@class_bp.route("/classes", methods=["GET"])
def get_classes():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class")
    classes = cursor.fetchall()
    cursor.close()
    return jsonify(classes)


@class_bp.route("/classes/<int:classID>", methods=["GET"])
def get_class(classID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class WHERE classID = %s", (classID,))
    cls = cursor.fetchone()
    cursor.close()

    if not cls:
        return jsonify({"error": "class not found"}), 404

    return jsonify(cls)


@class_bp.route("/classes/teacher/<int:teacherID>", methods=["GET"])
def get_teacher_classes(teacherID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Class WHERE teacherID = %s", (teacherID,))
    classes = cursor.fetchall()
    cursor.close()
    return jsonify(classes)


@class_bp.route("/classes/<int:classID>/students", methods=["GET"])
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


@class_bp.route("/classes", methods=["POST"])
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


@class_bp.route("/classes/<int:classID>", methods=["PUT"])
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


@class_bp.route("/classes/<int:classID>", methods=["DELETE"])
def delete_class(classID):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Class WHERE classID = %s", (classID,))
    db.commit()
    cursor.close()
    return jsonify({"message": "class deleted"})