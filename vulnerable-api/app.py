from flask import Flask, request, jsonify
import sqlite3
import jwt
import datetime

app = Flask(__name__)

SECRET_KEY = "supersecretkey"

# ---------- DATABASE INIT ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        balance INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- REGISTER ----------
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ❌ Пароль сохраняется в открытом виде
    c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, ?)",
              (username, password, 1000))

    conn.commit()
    conn.close()

    return jsonify({"message": "User created"})


# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ❌ SQL Injection
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    c.execute(query)

    user = c.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            "user_id": user[0],
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({"token": token})

    return jsonify({"error": "Invalid credentials"}), 401


# ---------- PROFILE (IDOR) ----------
@app.route("/profile/<int:user_id>", methods=["GET"])
def profile(user_id):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ❌ Нет проверки владельца
    c.execute("SELECT id, username, balance FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()

    conn.close()

    if user:
        return jsonify({
            "id": user[0],
            "username": user[1],
            "balance": user[2]
        })

    return jsonify({"error": "User not found"}), 404


# ---------- TRANSFER (нет авторизации) ----------
@app.route("/transfer", methods=["POST"])
def transfer():
    data = request.json
    from_id = data.get("from_id")
    to_id = data.get("to_id")
    amount = data.get("amount")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # ❌ Нет проверки токена
    # ❌ Нет проверки баланса

    c.execute("UPDATE users SET balance = balance - ? WHERE id = ?", (amount, from_id))
    c.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, to_id))

    conn.commit()
    conn.close()

    return jsonify({"message": "Transfer completed"})


if name == "__main__":
    app.run(debug=True)
