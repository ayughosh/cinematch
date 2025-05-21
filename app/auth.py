from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import re
from app.user import User
from app.database_utils import get_db_connection

auth = Blueprint("auth", __name__)


@auth.route("/profile")
@login_required
def profile():
    return "This is your private profile!"


# Register
@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            flash("Please enter a valid email address.")
            return redirect(url_for("auth.register"))

        password = request.form["password"]

        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email already registered.")
            return redirect(url_for("auth.register"))

        cur.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
            (username, email, password_hash),
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        user = User(user_id, username, email)
        login_user(user)
        return redirect(url_for("main.home"))

    return render_template("register.html")


# Login
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username, password_hash FROM users WHERE email = %s", (email,)
        )
        user_row = cur.fetchone()
        cur.close()
        conn.close()

        if user_row and check_password_hash(user_row[2], password):
            user = User(user_row[0], user_row[1], email)
            login_user(user)
            return redirect(url_for("main.home"))
        else:
            flash("Invalid credentials")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


# Logout
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("main.home"))
