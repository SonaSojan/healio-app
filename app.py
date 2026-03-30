from flask import Flask, render_template, request, redirect, session
from database import get_db_connection, create_table
from severity import detect_severity
import random

app = Flask(__name__)
app.secret_key = "healio_secret"

create_table()

# HOME
@app.route("/")
def home():
    return render_template("home.html")


# USER LOGIN
@app.route("/user-login")
def user_login():
    return render_template("user_login.html")


# USER DASHBOARD
@app.route("/user", methods=["GET", "POST"])
def user():
    if "user_id" not in session:
        session["user_id"] = "HLO-" + str(random.randint(1000, 9999))

    if request.method == "POST":
        symptoms = request.form.get("symptoms")
        message = request.form.get("message")

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

    return render_template("user_dashboard.html",
                           user_id=session["user_id"],
                           messages=messages)


# DOCTOR LOGIN
@app.route("/doctor-login", methods=["GET", "POST"])
def doctor_login():
    if request.method == "POST":
        if request.form["username"] == "doctor" and request.form["password"] == "healio2026":
            return redirect("/doctor")
    return render_template("doctor_login.html")


# DOCTOR DASHBOARD
@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    conn = get_db_connection()

    if request.method == "POST":
        emergency = 1 if "emergency" in request.form else 0

        conn.execute(
            "UPDATE messages SET reply=?, emergency=? WHERE id=?",
            (request.form["reply"], emergency, request.form["msg_id"])
        )
        conn.commit()

    messages = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("doctor_dashboard.html", messages=messages)


if __name__ == "__main__":
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)