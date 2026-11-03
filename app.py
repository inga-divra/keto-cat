import re
import secrets
import sqlite3
from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import config
import users

app = Flask(__name__)
app.secret_key = config.secret_key

USERNAME_PATTERN = r"[A-Za-z0-9_-]{3,20}"
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session.get("csrf_token"):
        abort(403)

@app.before_request
def add_csrf_token():
    # Every visitor gets a token, so that the register and login forms
    # are protected too, not only the forms of logged-in users.
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("register.html", filled={})

    check_csrf()
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    filled = {"username": username}

    if not re.fullmatch(USERNAME_PATTERN, username):
        flash("Username must be 3–20 characters: letters, numbers, - or _.")
        return render_template("register.html", filled=filled)
    if not PASSWORD_MIN_LENGTH <= len(password1) <= PASSWORD_MAX_LENGTH:
        flash(f"Password must be {PASSWORD_MIN_LENGTH}–{PASSWORD_MAX_LENGTH} characters long.")
        return render_template("register.html", filled=filled)
    if password1 != password2:
        flash("The passwords don't match. Please try again!")
        return render_template("register.html", filled=filled)

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("Oh no, that username is already taken. Please pick another one!")
        return render_template("register.html", filled=filled)

    flash("Your account was created. Welcome! Please log in.")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html", filled={})

    check_csrf()
    username = request.form["username"]
    password = request.form["password"]

    user = users.check_login(username, password)
    if not user:
        flash("Wrong username or password.")
        return render_template("login.html", filled={"username": username})

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["csrf_token"] = secrets.token_hex(16)
    flash(f"Welcome back, {user['username']}!")
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    require_login()
    check_csrf()
    session.clear()
    flash("You have logged out. See you again soon!")
    return redirect("/")
