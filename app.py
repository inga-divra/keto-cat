import math
import re
import secrets
import sqlite3
from flask import Flask
from flask import abort, flash, redirect, render_template, request, session, url_for
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
PAGE_SIZE = 10
COMMENT_MAX_LENGTH = 1000
RATINGS = ["1", "2", "3", "4", "5"]

TASTE = "Taste"

# Classification groups in the order they are shown. The options of each
# group come from the classes table. (title, several values allowed, required)
CLASS_GROUPS = [
    ("Taste", False, True),
    ("Diet", False, False),
    ("Meal", False, False),
    ("Restrictions", True, False),
]

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

def get_class_groups():
    options = {}
    for option in recipes.get_all_classes():
        options.setdefault(option["title"], []).append(option)
    return [{"title": title, "multiple": multiple, "required": required,
             "options": options.get(title, [])}
            for title, multiple, required in CLASS_GROUPS]

def empty_classes():
    return {title: [] for title, _, _ in CLASS_GROUPS}

def group_recipe_classes(recipe_id):
    groups = empty_classes()
    for recipe_class in recipes.get_recipe_classes(recipe_id):
        if recipe_class["title"] in groups:
            groups[recipe_class["title"]].append(recipe_class)
    return groups

def read_recipe_form():
    classes = {}
    for title, _, _ in CLASS_GROUPS:
        # dict.fromkeys drops repeated values, "" means "not specified".
        values = request.form.getlist(title.lower())
        classes[title] = [value for value in dict.fromkeys(values) if value]
    return {
        "title": request.form["title"].strip(),
        "ingredients": request.form["ingredients"].strip(),
        "instructions": request.form["instructions"].strip(),
        "classes": classes
    }

def selected_class_ids(filled):
    return [int(value) for values in filled["classes"].values() for value in values]

def recipe_form_error(filled, class_groups):
    if not filled["title"] or len(filled["title"]) > TITLE_MAX_LENGTH:
        return f"The title must be 1–{TITLE_MAX_LENGTH} characters long."
    if not filled["ingredients"] or len(filled["ingredients"]) > INGREDIENTS_MAX_LENGTH:
        return f"The ingredients must be 1–{INGREDIENTS_MAX_LENGTH} characters long."
    if not filled["instructions"] or len(filled["instructions"]) > INSTRUCTIONS_MAX_LENGTH:
        return f"The instructions must be 1–{INSTRUCTIONS_MAX_LENGTH} characters long."

    # Every value must be an option of its own group, so a forged form
    # cannot save an unknown class or a class of another group.
    for group in class_groups:
        values = filled["classes"][group["title"]]
        option_ids = [str(option["id"]) for option in group["options"]]
        name = group["title"].lower()
        if any(value not in option_ids for value in values):
            return f"Please choose a valid {name} option."
        if len(values) > 1 and not group["multiple"]:
            return f"Please choose only one {name} option."
        if group["required"] and not values:
            return f"Please choose a {name} for your recipe."
    return None

def get_own_comment(comment_id):
    comment = recipes.get_comment(comment_id)
    if not comment:
        abort(404)
    if comment["user_id"] != session["user_id"]:
        abort(403)
    return comment

def read_comment_form():
    return {
        "content": request.form.get("content", "").strip(),
        "rating": request.form.get("rating", "")
    }

def comment_form_error(filled):
    if not filled["content"] or len(filled["content"]) > COMMENT_MAX_LENGTH:
        return f"The comment must be 1–{COMMENT_MAX_LENGTH} characters long."
    if filled["rating"] not in RATINGS:
        return "Please rate the recipe from 1 to 5."
    return None

def render_recipe_page(recipe, filled=None, error=None):
    recipe_id = recipe["id"]
    user_id = session.get("user_id")
    # Guests and recipe owners cannot review, and nobody can review twice.
    can_review = (user_id is not None and user_id != recipe["user_id"]
                  and not recipes.has_comment(recipe_id, user_id))
    return render_template("recipe.html", recipe=recipe,
                           classes=group_recipe_classes(recipe_id),
                           comments=recipes.get_comments(recipe_id),
                           rating=recipes.get_rating(recipe_id),
                           can_review=can_review, filled=filled or {}, error=error)

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

    taste_id = taste["id"] if taste else None
    recipe_count = recipes.recipe_count(keyword, taste_id)
    page_count = max(math.ceil(recipe_count / PAGE_SIZE), 1)

    # An invalid page (abc, -1, 1.5) shows page 1 and a too big page number
    # shows the last page. The redirect keeps the search and the taste filter.
    page_value = request.args.get("page", "1")
    if re.fullmatch(r"[0-9]+", page_value):
        # Very long numbers are not converted, they are simply too big.
        page = int(page_value) if len(page_value) <= 9 else page_count
        page = min(max(page, 1), page_count)
    else:
        page = 1
    if page_value != str(page):
        return redirect(url_for("show_recipes", q=keyword or None,
                                taste=taste["value"] if taste else None,
                                page=page if page > 1 else None))

    found_recipes = recipes.get_recipes(keyword, taste_id, page, PAGE_SIZE)
    return render_template("recipes.html", recipes=found_recipes,
                           tastes=recipes.get_classes(TASTE),
                           keyword=keyword, taste=taste, recipe_count=recipe_count,
                           page=page, page_count=page_count)

@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id):
    recipe = recipes.get_recipe(recipe_id)
    if not recipe:
        abort(404)
    return render_recipe_page(recipe)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    recipe_count = users.get_recipe_count(user_id)
    comment_count = users.get_comment_count(user_id)
    user_recipes = users.get_recipes(user_id)
    return render_template("user.html", user=user, recipe_count=recipe_count,
                           comment_count=comment_count, recipes=user_recipes)

@app.route("/new_recipe", methods=["GET", "POST"])
def new_recipe():
    require_login()
    class_groups = get_class_groups()

    if request.method == "GET":
        return render_template("new_recipe.html", filled={"classes": empty_classes()},
                               class_groups=class_groups)

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled, class_groups)
    if error:
        flash(error)
        return render_template("new_recipe.html", filled=filled,
                               class_groups=class_groups)

    recipe_id = recipes.add_recipe(session["user_id"], filled["title"],
                                   filled["ingredients"], filled["instructions"],
                                   selected_class_ids(filled))
    flash("Purr-fect! Your recipe was added.")
    return redirect(f"/recipe/{recipe_id}")

@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    require_login()
    recipe = get_own_recipe(recipe_id)
    class_groups = get_class_groups()

    if request.method == "GET":
        filled = dict(recipe)
        filled["classes"] = {title: [str(recipe_class["id"]) for recipe_class in values]
                             for title, values in group_recipe_classes(recipe_id).items()}
        return render_template("edit_recipe.html", recipe=recipe, filled=filled,
                               class_groups=class_groups)

    check_csrf()
    filled = read_recipe_form()
    error = recipe_form_error(filled, class_groups)
    if error:
        flash(error)
        return render_template("edit_recipe.html", recipe=recipe, filled=filled,
                               class_groups=class_groups)

    recipes.update_recipe(recipe_id, filled["title"],
                          filled["ingredients"], filled["instructions"],
                          selected_class_ids(filled))
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

@app.route("/new_comment", methods=["POST"])
def new_comment():
    require_login()
    check_csrf()
    recipe = recipes.get_recipe(request.form.get("recipe_id", 0, type=int))
    if not recipe:
        abort(404)
    if recipe["user_id"] == session["user_id"]:
        abort(403)

    recipe_id = recipe["id"]
    already_reviewed = "You have already reviewed this recipe. You can edit your review instead."
    if recipes.has_comment(recipe_id, session["user_id"]):
        flash(already_reviewed)
        return redirect(f"/recipe/{recipe_id}#reviews")

    filled = read_comment_form()
    error = comment_form_error(filled)
    if error:
        return render_recipe_page(recipe, filled, error)

    try:
        recipes.add_comment(recipe_id, session["user_id"], filled["content"],
                            int(filled["rating"]))
    except sqlite3.IntegrityError:
        # Another request saved a review for the same user and recipe first.
        flash(already_reviewed)
        return redirect(f"/recipe/{recipe_id}#reviews")

    flash("Thank you for your review! Purr...")
    return redirect(f"/recipe/{recipe_id}#reviews")

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    require_login()
    comment = get_own_comment(comment_id)

    if request.method == "GET":
        filled = {"content": comment["content"], "rating": str(comment["rating"])}
        return render_template("edit_comment.html", comment=comment, filled=filled)

    check_csrf()
    filled = read_comment_form()
    error = comment_form_error(filled)
    if error:
        flash(error)
        return render_template("edit_comment.html", comment=comment, filled=filled)

    recipes.update_comment(comment_id, filled["content"], int(filled["rating"]))
    flash("Your review was updated.")
    return redirect(f"/recipe/{comment['recipe_id']}#reviews")

@app.route("/delete_comment/<int:comment_id>", methods=["GET", "POST"])
def delete_comment(comment_id):
    require_login()
    comment = get_own_comment(comment_id)

    if request.method == "GET":
        return render_template("delete_comment.html", comment=comment)

    check_csrf()
    recipes.remove_comment(comment_id)
    flash("Your review was deleted.")
    return redirect(f"/recipe/{comment['recipe_id']}#reviews")

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
