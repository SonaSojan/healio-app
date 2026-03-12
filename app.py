from flask import Flask, render_template, request, session
from severity import detect_severity
from database import get_db_connection, create_table
import random

app = Flask(__name__)
app.secret_key = "healio_secret_key"

create_table()   # Create database table on startup

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        session["user_id"] = "USER-" + str(random.randint(1000, 9999))

    emergency = False

    if request.method == "POST":

        # Symptoms submission
        if "symptoms" in request.form:
            severity = detect_severity(request.form["symptoms"])
            session["last_severity"] = severity
            if severity == "Severe":
                emergency = True

        # Message submission
        if "message" in request.form and "last_severity" in session:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO messages (user_id, message, severity, reply) VALUES (?, ?, ?, ?)",
                (session["user_id"], request.form["message"], session["last_severity"], "")
            )
            conn.commit()
            conn.close()

    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages").fetchall()
    conn.close()

    return render_template(
        "index.html",
        user_id=session["user_id"],
        emergency=emergency,
        messages=messages
    )

@app.route("/doctor", methods=["GET", "POST"])
def doctor():
    conn = get_db_connection()

    if request.method == "POST":
        conn.execute(
            "UPDATE messages SET reply = ? WHERE id = ?",
            (request.form["reply"], request.form["msg_id"])
        )
        conn.commit()

    messages = conn.execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("doctor.html", messages=messages)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
