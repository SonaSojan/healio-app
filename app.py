from flask import Flask, render_template, request, session, redirect
from severity import detect_severity
from database import get_db_connection, create_table
from whitenoise import WhiteNoise
import random

app = Flask(__name__)
app.secret_key = "healio_secret_key"

# Serve static files (important for Render)
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static")

# Create DB table
create_table()

# ===============================
# 🟦 LANDING PAGE
# ===============================
@app.route("/home")
def home():
    return render_template("home.html")


# ===============================
# 🟦 USER APP
# ===============================
@app.route("/app", methods=["GET", "POST"])
def user_app():

    # Create anonymous user ID
    if "user_id" not in session:
        session["user_id"] = "USER-" + str(random.randint(1000, 9999))

    # Handle form submission
    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        message = request.form.get("message")

        if symptoms:
            severity = detect_severity(symptoms)

            conn = get_db_connection()
            conn.execute(
                """
                INSERT INTO messages 
                (user_id, symptoms, message, severity, reply, emergency) 
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (session["user_id"], symptoms, message, severity, "", 0)
            )
            conn.commit()
            conn.close()

    # Fetch ONLY this user's messages
    conn = get_db_connection()
    messages = conn.execute(
        "SELECT * FROM messages WHERE user_id=? ORDER BY id ASC",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    # Check if doctor marked emergency
    emergency = any(msg["emergency"] == 1 for msg in messages)

    return render_template(
        "index.html",
        user_id=session["user_id"],
        messages=messages,
        emergency=emergency
    )


# ===============================
# 🟦 DOCTOR LOGIN
# ===============================
@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "doctor" and password == "healio2026":
            return redirect("/doctor")

    return render_template("doctor_login.html")


# ===============================
# 🟦 DOCTOR DASHBOARD
# ===============================
@app.route("/doctor", methods=["GET", "POST"])
def doctor():

    conn = get_db_connection()

    # Handle reply
    if request.method == "POST":
        reply = request.form.get("reply")
        msg_id = request.form.get("msg_id")
        emergency_flag = 1 if "emergency" in request.form else 0

        conn.execute(
            "UPDATE messages SET reply=?, emergency=? WHERE id=?",
            (reply, emergency_flag, msg_id)
        )
        conn.commit()

    # Sort by severity priority
    messages = conn.execute("""
        SELECT * FROM messages
        ORDER BY
            CASE severity
                WHEN 'Severe' THEN 1
                WHEN 'Moderate' THEN 2
                ELSE 3
            END,
            id DESC
    """).fetchall()

    conn.close()

    return render_template("doctor.html", messages=messages)


# ===============================
# 🟦 DEFAULT ROUTE
# ===============================
@app.route("/")
def default():
    return redirect("/home")


# ===============================
# 🟦 RUN APP
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)