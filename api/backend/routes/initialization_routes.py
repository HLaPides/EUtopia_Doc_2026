from flask import Blueprint, request, jsonify
from backend.db_connection import get_db


apiinit_bp = Blueprint("apiinit", __name__)


@apiinit_bp.route("/users", methods=["GET"])
def get_users():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    cursor.close()
    return jsonify(users)


@apiinit_bp.route("/users/<int:userID>", methods=["GET"])
def get_user(userID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Users WHERE userID = %s", (userID,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify(user)


@apiinit_bp.route("/roles", methods=["GET"])
def get_roles():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Roles")
    roles = cursor.fetchall()
    cursor.close()
    return jsonify(roles)


@apiinit_bp.route("/users/<int:userID>/roles", methods=["GET"])
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


@apiinit_bp.route("/users/by-role/<roleName>", methods=["GET"])
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





# ── Progress & Simulations ────────────────────────────────────────────────────

@apiinit_bp.route("/progress/<int:studentID>", methods=["GET"])
def get_student_progress(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StudentProgress WHERE studentID = %s", (studentID,))
    progress = cursor.fetchall()
    cursor.close()
    return jsonify(progress)


@apiinit_bp.route("/simulations/<int:studentID>", methods=["GET"])
def get_student_simulations(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Simulation WHERE studentID = %s", (studentID,))
    simulations = cursor.fetchall()
    cursor.close()
    return jsonify(simulations)





# ── Students ──────────────────────────────────────────────────────────────────

@apiinit_bp.route("/students/<int:studentID>/profile", methods=["GET"])
def get_student_profile(studentID):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM StudentProfile WHERE studentID = %s", (studentID,))
    profile = cursor.fetchone()
    cursor.close()

    if not profile:
        return jsonify({"error": "profile not found"}), 404

    return jsonify(profile)


@apiinit_bp.route("/simulations", methods=["POST"])
def create_simulation():
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Simulation
        (
            studentID,
            countryName,
            population,
            unemploymentRate,
            compulsoryVoting,
            medianAge,
            region,
            nationalTurnout,
            predictedTurnout,
            createdBy,
            updatedBy
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        data["studentID"],
        data["countryName"],
        data["population"],
        data["unemploymentRate"],
        data["compulsoryVoting"],
        data["medianAge"],
        data["region"],
        data["nationalTurnout"],
        data["predicted_turnout"],
        data["studentID"],
        data["studentID"],
    ))

    db.commit()
    cursor.close()

    return jsonify({"message": "simulation saved"}), 201