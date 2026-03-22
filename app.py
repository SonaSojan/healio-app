from flask import Flask, render_template, request, session, redirect
from severity import detect_severity
from database import get_db_connection, create_table
from whitenoise import WhiteNoise
import random

app = Flask(__name__)
app.secret_key = "healio_secret_key"

# Serve static files on Render
app.wsgi_app = WhiteNoise(app.wsgi_app, root="static")

create_table()

# 🟦 LANDING PAGE (Figma UI)
@app.route("/home")
def landing():
    return render_template("home.html")


# 🟦 USER APP (your main logic moved here)
@app.route("/app", methods=["GET", "POST"])
def user_app():

    if "user_id" not in session:
        session["user_id"] = "USER-" + str(random.randint(1000, 9999))

    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        message = request.form.get("message")

        if symptoms and message:
            severity = detect_severity(symptoms)

            conn = get_db_connection()
            conn.execute(
                "INSERT INTO messages (user_id, message, severity, reply, emergency) VALUES (?, ?, ?, ?, ?)",
                (session["user_id"], message, severity, "", 0)
            )
            conn.commit()
            conn.close()

    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages").fetchall()
    conn.close()

    emergency = any(
        msg["emergency"] == 1 and msg["user_id"] == session["user_id"]
        for msg in messages
    )

    return render_template(
        "index.html",
        user_id=session["user_id"],
        messages=messages,
        emergency=emergency
    )


# 🟦 DOCTOR LOGIN PAGE
@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        if request.form["username"] == "doctor" and request.form["password"] == "healio2026":
            return redirect("/doctor")
    return render_template("doctor_login.html")


# 🟦 DOCTOR DASHBOARD
@app.route("/doctor", methods=["GET", "POST"])
def doctor():

    conn = get_db_connection()

    if request.method == "POST":
        emergency_flag = 1 if "emergency" in request.form else 0

        conn.execute(
            "UPDATE messages SET reply = ?, emergency = ? WHERE id = ?",
            (request.form["reply"], emergency_flag, request.form["msg_id"])
        )
        conn.commit()

    messages = conn.execute("""
    SELECT * FROM messages
    ORDER BY
        CASE severity
            WHEN 'Severe' THEN 1
            WHEN 'Moderate' THEN 2
            ELSE 3
        END
    """).fetchall()

    conn.close()

    return render_template("doctor.html", messages=messages)


# 🟦 DEFAULT ROUTE → LANDING PAGE
@app.route("/")
def default():
    return redirect("/home")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)