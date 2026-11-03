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
SEARCH_MAX_LENGTH = 100

TASTE = "Taste"

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
        "instructions": request.form["instructions"].strip(),
        "taste": request.form.get("taste", "")
    }

def get_recipe_taste(recipe_id):
    for recipe_class in recipes.get_recipe_classes(recipe_id):
        if recipe_class["title"] == TASTE:
            return recipe_class
    return None

def recipe_form_error(filled):
    if not filled["title"] or len(filled["title"]) > TITLE_MAX_LENGTH:
        return f"The title must be 1–{TITLE_MAX_LENGTH} characters long."
    if not filled["ingredients"] or len(filled["ingredients"]) > INGREDIENTS_MAX_LENGTH:
        return f"The ingredients must be 1–{INGREDIENTS_MAX_LENGTH} characters long."
    if not filled["instructions"] or len(filled["instructions"]) > INSTRUCTIONS_MAX_LENGTH:
        return f"The instructions must be 1–{INSTRUCTIONS_MAX_LENGTH} characters long."

    taste_ids = [str(taste["id"]) for taste in recipes.get_classes(TASTE)]
    if filled["taste"] not in taste_ids:
        return "Please choose a taste for your recipe."
    return None

@app.before_request
def add_csrf_token():
    # Every visitor gets a token, so that the register and login forms
    # are protected too, not only the forms of logged-in users.
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404

@app.route("/")
def index():
    tastes = recipes.get_classes(TASTE)
    taste_value = request.args.get("taste")
    if not taste_value:
        return render_template("index.html", tastes=tastes)

    taste = recipes.get_class(TASTE, taste_value)
    if not taste:
        abort(404)

    # Try not to suggest the same recipe twice in a row.
    previous_id = request.args.get("previous", 0, type=int)
    suggestion = recipes.get_random_recipe(taste["id"], previous_id)
    if not suggestion:
        suggestion = recipes.get_random_recipe(taste["id"])

    return render_template("index.html", tastes=tastes, taste=taste,
                           suggestion=suggestion)

@app.route("/recipes")
def show_recipes():
    keyword = request.args.get("q", "").strip()
    if len(keyword) > SEARCH_MAX_LENGTH:
        flash(f"The search can be at most {SEARCH_MAX_LENGTH} characters long.")
        keyword = keyword[:SEARCH_MAX_LENGTH]

    taste = None
    taste_value = request.args.get("taste")
    if taste_value:
        taste = recipes.get_class(TASTE, taste_value)
        if not taste:
            abort(404)

    found_recipes = recipes.get_recipes(keyword, taste["id"] if taste else None)
    return render_template("recipes.html", recipes=found_recipes,
                           tastes=recipes.get_classes(TASTE),
                           keyword=keyword, taste=taste)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    taste = get_recipe_taste(recipe_id)
    return render_template("recipe.html", recipe=recipe, taste=taste)

@app.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    require_login()
    tastes = recipes.get_classes(TASTE)

    if request.method == "GET":
        return render_template("new_recipe.html", filled={}, tastes=tastes)

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled)
    if error:
        flash(error)
        return render_template("new_recipe.html", filled=filled, tastes=tastes)

    recipe_id = recipes.add_recipe(session["user_id"], filled["title"],
                                   filled["ingredients"], filled["instructions"],
                                   [int(filled["taste"])])
    flash("Purr-fect! Your recipe was added.")
    return redirect(f"/recipe/{recipe_id}")

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    require_login()
    recipe = get_own_recipe(recipe_id)
    tastes = recipes.get_classes(TASTE)

    if request.method == "GET":
        filled = dict(recipe)
        taste = get_recipe_taste(recipe_id)
        filled["taste"] = str(taste["id"]) if taste else ""
        return render_template("edit_recipe.html", recipe=recipe, filled=filled,
                               tastes=tastes)

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled)
    if error:
        flash(error)
        return render_template("edit_recipe.html", recipe=recipe, filled=filled,
                               tastes=tastes)

    recipes.update_recipe(recipe_id, filled["title"],
                          filled["ingredients"], filled["instructions"],
                          [int(filled["taste"])])
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
