from flask import Flask, request, jsonify
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

app = Flask(__name__)

# ---------------- JWT CONFIG ----------------
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="apartmentdb",
        user="postgres",
        password="charitha@30"
    )


# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])  # hash password
    role = data.get('role', 'user')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cur.fetchone():
        cur.close()
        conn.close()
        return jsonify({"message": "Email already registered"}), 400

    cur.execute(
        "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
        (name, email, password, role)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User registered successfully"})


# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, role, password FROM users WHERE email=%s", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user[2], password):  # verify hash
        access_token = create_access_token(
            identity=str(user[0]),
            additional_claims={"role": user[1]}
        )
        return jsonify(access_token=access_token)

    return jsonify({"message": "Invalid credentials"}), 401


# ---------------- ADD TOWER (ADMIN) ----------------
@app.route('/add_tower', methods=['POST'])
@jwt_required()
def add_tower():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    name = data['name']
    total_units = data['total_units']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO towers (name, total_units) VALUES (%s, %s)", (name, total_units))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Tower added successfully"})

@app.route('/add_unit', methods=['POST'])
@jwt_required()
def add_unit():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    tower_id = data['tower_id']
    unit_number = data['unit_number']
    rent = data['rent']

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO units (tower_id, unit_number, rent, is_available) VALUES (%s, %s, %s, TRUE)",
        (tower_id, unit_number, rent)
    )

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Unit added successfully"})


@app.route('/book_unit', methods=['POST'])
@jwt_required()
def book_unit():
    user_id = get_jwt_identity()
    data = request.get_json()
    unit_id = data['unit_id']

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if unit is available
    cur.execute("SELECT is_available FROM units WHERE id=%s", (unit_id,))
    unit = cur.fetchone()
    if not unit:
        cur.close()
        conn.close()
        return jsonify({"message": "Unit not found"}), 404
    if not unit[0]:
        cur.close()
        conn.close()
        return jsonify({"message": "Unit already occupied"}), 400

    cur.execute("INSERT INTO bookings (user_id, unit_id, status) VALUES (%s, %s, 'pending')",
                (user_id, unit_id))

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Booking requested"})


@app.route('/approve_booking/<int:booking_id>', methods=['PUT'])
@jwt_required()
def approve_booking(booking_id):
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    # Get unit id
    cur.execute("SELECT unit_id FROM bookings WHERE id=%s", (booking_id,))
    unit = cur.fetchone()

    if not unit:
        return jsonify({"message": "Booking not found"}), 404

    unit_id = unit[0]

    # Approve booking
    cur.execute("UPDATE bookings SET status='approved' WHERE id=%s", (booking_id,))

    # Mark unit as occupied
    cur.execute("UPDATE units SET is_available=FALSE WHERE id=%s", (unit_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Booking approved"})

# ---------------- VIEW MY BOOKINGS (USER) ----------------
@app.route('/my_bookings', methods=['GET'])
@jwt_required()
def my_bookings():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bookings WHERE user_id=%s", (user_id,))
    bookings = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for booking in bookings:
        result.append({
            "id": booking[0],
            "unit_id": booking[2],
            "status": booking[3]
        })

    return jsonify(result)

# ---------------- ADD AMENITY (ADMIN) ----------------
@app.route('/add_amenity', methods=['POST'])
@jwt_required()
def add_amenity():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    name = data['name']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO amenities (name) VALUES (%s)", (name,))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Amenity added successfully"})

# ---------------- VIEW AMENITIES ----------------
@app.route('/amenities', methods=['GET'])
def view_amenities():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM amenities")
    amenities = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for amenity in amenities:
        result.append({
            "id": amenity[0],
            "name": amenity[1]
        })

    return jsonify(result)

@app.route('/tower_occupancy_report', methods=['GET'])
@jwt_required()
def tower_occupancy_report():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.name, COUNT(u.id) as total_units,
        SUM(CASE WHEN u.is_available = FALSE THEN 1 ELSE 0 END) as occupied_units
        FROM towers t
        LEFT JOIN units u ON t.id = u.tower_id
        GROUP BY t.id, t.name
    """)
    report = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for row in report:
        result.append({
            "tower": row[0],
            "total_units": row[1],
            "occupied_units": row[2]
        })

    return jsonify(result)

@app.route("/occupancy_report", methods=["GET"])
@jwt_required()
def occupancy_report():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    # Total units
    cur.execute("SELECT COUNT(*) FROM units")
    total_units = cur.fetchone()[0]

    # Available units
    cur.execute("SELECT COUNT(*) FROM units WHERE is_available = TRUE")
    available = cur.fetchone()[0]

    # Occupied units
    cur.execute("SELECT COUNT(*) FROM units WHERE is_available = FALSE")
    occupied = cur.fetchone()[0]

    cur.close()
    conn.close()

    return jsonify({
        "total_units": total_units,
        "available_units": available,
        "occupied_units": occupied
    })

@app.route('/revenue_report', methods=['GET'])
@jwt_required()
def revenue_report():
    if get_jwt()["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403

    conn = get_db_connection()
    cur = conn.cursor()

    # Total revenue
    cur.execute("""
        SELECT COALESCE(SUM(u.rent), 0) 
        FROM bookings b 
        JOIN units u ON b.unit_id = u.id
        WHERE b.status='approved'
    """)
    total_revenue = cur.fetchone()[0]

    # Revenue per tower
    cur.execute("""
        SELECT t.name, COALESCE(SUM(u.rent), 0)
        FROM bookings b
        JOIN units u ON b.unit_id = u.id
        JOIN towers t ON u.tower_id = t.id
        WHERE b.status='approved'
        GROUP BY t.id, t.name
    """)
    tower_revenue = [{"tower": row[0], "revenue": row[1]} for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "total_revenue": total_revenue,
        "revenue_per_tower": tower_revenue
    })


if __name__ == '__main__':
    app.run(debug=True)
