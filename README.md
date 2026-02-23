# 🏢 Apartment Rental Management Backend

A role-based Apartment Rental Management System built using Flask, PostgreSQL, and JWT Authentication.

---

## 🚀 Features

### 🔐 Authentication
- User Registration
- Login with JWT Token
- Secure Password Hashing

### 👥 Role-Based Access Control
- Admin-only routes
- User-only routes
- JWT role claims validation

### 🏢 Admin Functionalities
- Add Towers
- Add Units
- Approve Bookings
- Add Amenities
- Revenue Report
- Occupancy Report

### 👤 User Functionalities
- Book Unit
- View My Bookings

---

## 📊 Reports
- Revenue per Tower
- Total Revenue
- Occupancy Status

---

## 🛠 Tech Stack
- Python
- Flask
- PostgreSQL
- flask-jwt-extended
- psycopg2

---

## 📂 Project Structure
backend/
│
├── app/
│ ├── routes/
│ │ ├── auth.py
│ │ ├── admin.py
│ │ ├── user.py
│ │ └── reports.py
│ ├── config.py
│ ├── db.py
│ └── init.py
│
├── run.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .gitignore

---

## 🧪 API Testing
All endpoints tested using Postman.

---

## 👩‍💻 Author
**Charitha B Naik**
