from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "timeswap_secret_key"

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ---------------- HOME ---------------- #

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER ---------------- #

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        try:

            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            skills_offered = request.form["skills_offered"]
            skills_needed = request.form["skills_needed"]

            conn = sqlite3.connect("timeswap.db")
            cursor = conn.cursor()

            cursor.execute("""
            INSERT INTO users
            (name,email,password,skills_offered,skills_needed)
            VALUES(?,?,?,?,?)
            """,
            (name,email,password,
             skills_offered,skills_needed))

            conn.commit()
            conn.close()

            return redirect("/login")

        except sqlite3.IntegrityError:
            return "Email already exists!"

    return render_template("register.html")


# ---------------- LOGIN ---------------- #

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("timeswap.db")
        cursor = conn.cursor()

        cursor.execute("""
        SELECT *
        FROM users
        WHERE email=? AND password=?
        """, (email, password))

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user_id"] = user[0]
            session["user_name"] = user[1]

            return redirect("/dashboard")

        else:
            return "Invalid Email or Password!"

    return render_template("login.html")


# ---------------- LOGOUT ---------------- #

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")
# ---------------- DASHBOARD ---------------- #

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("timeswap.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
    SELECT name,credits,reputation
    FROM users
    WHERE id=?
    """, (user_id,))

    user = cursor.fetchone()

    cursor.execute("""
    SELECT *
    FROM questions
    ORDER BY id DESC
    """)

    questions = cursor.fetchall()

    cursor.execute("""
    SELECT *
    FROM answers
    """)

    answer_rows = cursor.fetchall()

    answers = {}

    for row in answer_rows:

        question_id = row[1]

        if question_id not in answers:
            answers[question_id] = []

        answers[question_id].append(row)

    conn.close()

    return render_template(
        "dashboard.html",
        name=user[0],
        credits=user[1],
        reputation=user[2],
        questions=questions,
        answers=answers,
        current_user=session["user_name"]
    )
# ---------------- PROFILE ---------------- #

@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("timeswap.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
    SELECT name,credits,reputation
    FROM users
    WHERE id=?
    """, (user_id,))

    user = cursor.fetchone()

    cursor.execute("""
    SELECT COUNT(*)
    FROM questions
    WHERE username=?
    """, (user[0],))

    total_questions = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*)
    FROM answers
    WHERE username=?
    """, (user[0],))

    total_answers = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "profile.html",
        name=user[0],
        credits=user[1],
        reputation=user[2],
        total_questions=total_questions,
        total_answers=total_answers
    )
# ---------------- CREATE TASK ---------------- #

@app.route("/add_question", methods=["POST"])
def add_question():

    if "user_id" not in session:
        return redirect("/login")

    question = request.form["question"]

    reward = int(request.form["reward"])

    attachment_name = ""

    if "attachment" in request.files:

        file = request.files["attachment"]

        if file.filename != "":

            attachment_name = secure_filename(file.filename)

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    attachment_name
                )
            )

    conn = sqlite3.connect("timeswap.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
    SELECT name,credits
    FROM users
    WHERE id=?
    """, (user_id,))

    user = cursor.fetchone()

    username = user[0]
    credits = user[1]

    if credits < reward:

        conn.close()

        return "Not enough credits!"

    new_credits = credits - reward

    cursor.execute("""
    UPDATE users
    SET credits=?
    WHERE id=?
    """, (new_credits, user_id))

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    cursor.execute("""
    INSERT INTO questions
    (username,question,reward,attachment,date_posted)
    VALUES(?,?,?,?,?)
    """,
    (
        username,
        question,
        reward,
        attachment_name,
        current_time
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")
# ---------------- ADD ANSWER ---------------- #

@app.route("/add_answer/<int:question_id>",
           methods=["POST"])
def add_answer(question_id):

    if "user_id" not in session:
        return redirect("/login")

    answer = request.form["answer"]

    attachment_name = ""

    if "attachment" in request.files:

        file = request.files["attachment"]

        if file.filename != "":

            attachment_name = secure_filename(
                file.filename
            )

            file.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    attachment_name
                )
            )

    conn = sqlite3.connect("timeswap.db")
    cursor = conn.cursor()

    user_id = session["user_id"]

    cursor.execute("""
    SELECT name
    FROM users
    WHERE id=?
    """, (user_id,))

    username = cursor.fetchone()[0]

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    cursor.execute("""
    INSERT INTO answers
    (
        question_id,
        username,
        answer,
        attachment,
        date_posted
    )
    VALUES(?,?,?,?,?)
    """,
    (
        question_id,
        username,
        answer,
        attachment_name,
        current_time
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")
# ---------------- ACCEPT ANSWER ---------------- #

@app.route("/accept_answer/<int:answer_id>")
def accept_answer(answer_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("timeswap.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        question_id,
        username,
        accepted
    FROM answers
    WHERE id=?
    """, (answer_id,))

    answer = cursor.fetchone()

    if answer is None:

        conn.close()

        return redirect("/dashboard")

    question_id = answer[0]
    answer_user = answer[1]
    accepted = answer[2]

    if accepted == 1:

        conn.close()

        return redirect("/dashboard")

    cursor.execute("""
    SELECT reward
    FROM questions
    WHERE id=?
    """, (question_id,))

    reward = cursor.fetchone()[0]

    cursor.execute("""
    UPDATE users
    SET credits = credits + ?,
        reputation = reputation + 0.5
    WHERE name=?
    """, (reward, answer_user))

    cursor.execute("""
    UPDATE answers
    SET accepted=1
    WHERE id=?
    """, (answer_id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")
if __name__ == "__main__":
    app.run(debug=True)