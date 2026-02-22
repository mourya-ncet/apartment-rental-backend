from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.db import get_db_connection

user_bp = Blueprint("user", __name__)


# ✅ Book Unit
@user_bp.route("/book-unit", methods=["POST"])
@jwt_required()
def book_unit():
    user_id = get_jwt_identity()
    data = request.get_json()
    unit_id = data["unit_id"]

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if unit available
    cur.execute("SELECT is_available FROM units WHERE id=%s", (unit_id,))
    result = cur.fetchone()

    if not result:
        return jsonify({"message": "Unit not found"}), 404

    if not result[0]:
        return jsonify({"message": "Unit not available"}), 400

    cur.execute(
        "INSERT INTO bookings (user_id, unit_id, status) VALUES (%s, %s, %s)",
        (user_id, unit_id, "pending")
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Booking request sent"})


# ✅ View My Bookings
@user_bp.route("/my-bookings", methods=["GET"])
@jwt_required()
def my_bookings():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.id, u.unit_number, b.status
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        WHERE b.user_id = %s
    """, (user_id,))

    bookings = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for b in bookings:
        result.append({
            "booking_id": b[0],
            "unit_number": b[1],
            "status": b[2]
        })

    return jsonify(result)