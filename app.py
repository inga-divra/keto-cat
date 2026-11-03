import re
import secrets
import sqlite3
from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import config
import recipes
import users

app = Flask(__name__)
app.secret_key = config.secret_key

USERNAME_PATTERN = r"[A-Za-z0-9_-]{3,20}"
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

TITLE_MAX_LENGTH = 100
INGREDIENTS_MAX_LENGTH = 3000
INSTRUCTIONS_MAX_LENGTH = 5000

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session.get("csrf_token"):
        abort(403)

def get_own_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    if recipe["user_id"] != session["user_id"]:
        abort(403)
    return recipe

def read_recipe_form():
    return {
        "title": request.form["title"].strip(),
        "ingredients": request.form["ingredients"].strip(),
        "instructions": request.form["instructions"].strip()
    }

def recipe_form_error(filled):
    if not filled["title"] or len(filled["title"]) > TITLE_MAX_LENGTH:
        return f"The title must be 1–{TITLE_MAX_LENGTH} characters long."
    if not filled["ingredients"] or len(filled["ingredients"]) > INGREDIENTS_MAX_LENGTH:
        return f"The ingredients must be 1–{INGREDIENTS_MAX_LENGTH} characters long."
    if not filled["instructions"] or len(filled["instructions"]) > INSTRUCTIONS_MAX_LENGTH:
        return f"The instructions must be 1–{INSTRUCTIONS_MAX_LENGTH} characters long."
    return None

@app.before_request
def add_csrf_token():
    # Every visitor gets a token, so that the register and login forms
    # are protected too, not only the forms of logged-in users.
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/recipes")
def show_recipes():
    all_recipes = recipes.get_recipes()
    return render_template("recipes.html", recipes=all_recipes)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    return render_template("recipe.html", recipe=recipe)

@app.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    require_login()

    if request.method == "GET":
        return render_template("new_recipe.html", filled={})

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled)
    if error:
        flash(error)
        return render_template("new_recipe.html", filled=filled)

    recipe_id = recipes.add_recipe(session["user_id"], filled["title"],
                                   filled["ingredients"], filled["instructions"])
    flash("Purr-fect! Your recipe was added.")
    return redirect(f"/recipe/{recipe_id}")

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    require_login()
    recipe = get_own_recipe(recipe_id)

    if request.method == "GET":
        return render_template("edit_recipe.html", recipe=recipe, filled=recipe)

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled)
    if error:
        flash(error)
        return render_template("edit_recipe.html", recipe=recipe, filled=filled)

    recipes.update_recipe(recipe_id, filled["title"],
                          filled["ingredients"], filled["instructions"])
    flash("Your recipe was updated.")
    return redirect(f"/recipe/{recipe_id}")

@app.route("/delete_recipe/<int:recipe_id>", methods=["GET", "POST"])
def delete_recipe(recipe_id):
    require_login()
    recipe = get_own_recipe(recipe_id)

    if request.method == "GET":
        return render_template("delete_recipe.html", recipe=recipe)

    check_csrf()
    recipes.remove_recipe(recipe_id)
    flash("The recipe was deleted.")
    return redirect("/recipes")

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
