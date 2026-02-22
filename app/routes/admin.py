from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.db import get_db_connection

admin_bp = Blueprint("admin", __name__)

# Helper function to check admin role
def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True


# ✅ Add Tower
@admin_bp.route("/add-tower", methods=["POST"])
@jwt_required()
def add_tower():
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    data = request.get_json()
    name = data["name"]
    total_units = data["total_units"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO towers (name, total_units) VALUES (%s, %s)",
        (name, total_units)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Tower added successfully"})


# ✅ Add Unit
@admin_bp.route("/add-unit", methods=["POST"])
@jwt_required()
def add_unit():
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    data = request.get_json()
    tower_id = data["tower_id"]
    unit_number = data["unit_number"]
    rent = data["rent"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO units (tower_id, unit_number, rent, is_available) VALUES (%s, %s, %s, %s)",
        (tower_id, unit_number, rent, True)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Unit added successfully"})


# ✅ Approve / Decline Booking
@admin_bp.route("/approve-booking/<int:booking_id>", methods=["PUT"])
@jwt_required()
def approve_booking(booking_id):
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    # Approve booking
    cur.execute(
        "UPDATE bookings SET status='approved' WHERE id=%s RETURNING unit_id",
        (booking_id,)
    )
    result = cur.fetchone()

    if not result:
        return jsonify({"message": "Booking not found"}), 404

    unit_id = result[0]

    # Mark unit unavailable
    cur.execute(
        "UPDATE units SET is_available=False WHERE id=%s",
        (unit_id,)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Booking approved successfully"})


# ✅ Add Amenity
@admin_bp.route("/add-amenity", methods=["POST"])
@jwt_required()
def add_amenity():
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    data = request.get_json()
    name = data["name"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO amenities (name) VALUES (%s)",
        (name,)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Amenity added successfully"})