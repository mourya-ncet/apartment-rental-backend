from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.db import get_db_connection

reports_bp = Blueprint("reports", __name__)

def admin_required():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return False
    return True


# ✅ Revenue Report
@reports_bp.route("/revenue-report", methods=["GET"])
@jwt_required()
def revenue_report():
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.name, SUM(u.rent)
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN towers t ON u.tower_id = t.id
        WHERE b.status = 'approved'
        GROUP BY t.name
    """)

    rows = cur.fetchall()

    total_revenue = 0
    revenue_per_tower = []

    for row in rows:
        revenue_per_tower.append({
            "tower": row[0],
            "revenue": str(row[1])
        })
        total_revenue += row[1]

    cur.close()
    conn.close()

    return jsonify({
        "revenue_per_tower": revenue_per_tower,
        "total_revenue": str(total_revenue)
    })


# ✅ Occupancy Report
@reports_bp.route("/occupancy-report", methods=["GET"])
@jwt_required()
def occupancy_report():
    if not admin_required():
        return jsonify({"message": "Admins only"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE is_available = FALSE) AS occupied,
            COUNT(*) FILTER (WHERE is_available = TRUE) AS available
        FROM units
    """)

    result = cur.fetchone()
    cur.close()
    conn.close()

    return jsonify({
        "occupied_units": result[0],
        "available_units": result[1]
    })