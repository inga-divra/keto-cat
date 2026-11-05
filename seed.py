"""Create a large test database for performance testing.

The database is created from schema.sql and init.sql and filled with
generated users, recipes, classifications and reviews. The same --seed
always gives the same data.

Usage:
    python seed.py --database test-data/large.db
    python seed.py --database test-data/large.db --recipes 1000 --overwrite

The project's own database.db is never accepted as the target.
All generated users have the password "seedpassword".
"""
import argparse
import random
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
REAL_DATABASE = BASE_DIR / "database.db"
SQL_FILES = [BASE_DIR / "schema.sql", BASE_DIR / "init.sql"]
PASSWORD = "seedpassword"
FIRST_DATE = datetime(2024, 11, 1, 8, 0, 0)

SWEET_DISHES = ["Mug Cake", "Cheesecake", "Fat Bombs", "Chia Pudding", "Cookies",
                "Brownies", "Panna Cotta", "Muffins", "Pancakes", "Mousse",
                "Truffles", "Ice Cream"]
SAVORY_DISHES = ["Omelette", "Lasagna", "Salmon Bowl", "Meatballs", "Soup",
                 "Salad", "Frittata", "Pizza", "Burger Bowl", "Stir-Fry",
                 "Casserole", "Egg Muffins"]
SWEET_FLAVORS = ["Chocolate", "Almond", "Coconut", "Lemon", "Raspberry",
                 "Vanilla", "Cinnamon", "Peanut Butter", "Blueberry", "Espresso"]
SAVORY_FLAVORS = ["Cheesy", "Garlic", "Spinach", "Bacon", "Mushroom", "Avocado",
                  "Zucchini", "Chili", "Pesto", "Smoked Salmon"]
SWEET_INGREDIENTS = ["almond flour", "coconut flour", "cocoa powder", "dark chocolate",
                     "erythritol", "stevia", "coconut cream", "cream cheese",
                     "vanilla extract", "cinnamon", "raspberries", "blueberries",
                     "peanut butter", "chia seeds", "lemon zest", "espresso"]
SAVORY_INGREDIENTS = ["eggs", "cheddar", "mozzarella", "parmesan", "bacon", "salmon",
                      "ground beef", "chicken thighs", "spinach", "zucchini",
                      "mushrooms", "avocado", "garlic", "olive oil", "chili flakes",
                      "basil pesto", "cauliflower", "onion"]
COMMON_INGREDIENTS = ["butter", "salt", "heavy cream", "baking powder", "psyllium husk"]
STEPS = ["Preheat the oven to 180 °C.", "Mix the dry ingredients in a bowl.",
         "Whisk the wet ingredients together.", "Combine everything and stir well.",
         "Cook on medium heat for 10 minutes.", "Bake for 20–25 minutes.",
         "Let it cool for a while.", "Chill in the fridge for an hour.",
         "Season to taste and serve."]
REVIEWS = ["Delicious, will make again!", "A bit too sweet for me.",
           "Easy to make and tasty.", "My family loved it.",
           "Good, but I added more salt.", "Perfect for a quick breakfast.",
           "Texture was a little dry.", "Purr-fect keto treat!",
           "Nice recipe, thanks for sharing.", "Not my favourite, but okay."]

def parse_arguments():
    parser = argparse.ArgumentParser(description="Create a large Keto-Cat test database.")
    parser.add_argument("--database", required=True, type=Path,
                        help="path of the test database to create")
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--recipes", type=int, default=10_000)
    parser.add_argument("--reviews", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=2026, help="random seed")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace the test database if it already exists")
    return parser.parse_args()

def check_target(args):
    target = args.database.resolve()
    if target == REAL_DATABASE.resolve() or target.name == "database.db":
        sys.exit("Refusing to use database.db: give a separate test database path.")
    if target.is_dir():
        sys.exit(f"{target} is a directory.")
    if target.exists() and not args.overwrite:
        sys.exit(f"{target} already exists. Use --overwrite to replace it.")
    if args.users < 2:
        sys.exit("At least 2 users are needed, because nobody reviews their own recipe.")
    if args.recipes < 0 or args.reviews < 0:
        sys.exit("The numbers of recipes and reviews cannot be negative.")
    if args.reviews > args.recipes * (args.users - 1):
        sys.exit("Too many reviews: each user can review each other user's recipe once.")
    return target

def get_class_ids(con):
    class_ids = {}
    for class_id, title, value in con.execute("SELECT id, title, value FROM classes"):
        class_ids[(title, value)] = class_id
    return class_ids

def make_recipe(rng, recipe_id, users, class_ids):
    sweet = rng.random() < 0.5
    if sweet:
        title = f"{rng.choice(SWEET_FLAVORS)} {rng.choice(SWEET_DISHES)}"
        pool = SWEET_INGREDIENTS
        meals = [None, "Dessert", "Snack", "Breakfast"]
    else:
        title = f"{rng.choice(SAVORY_FLAVORS)} {rng.choice(SAVORY_DISHES)}"
        pool = SAVORY_INGREDIENTS
        meals = [None, "Main course", "Breakfast", "Snack"]

    ingredients = rng.sample(pool, rng.randint(3, 6)) + rng.sample(COMMON_INGREDIENTS, 2)
    ingredient_text = "\n".join(f"{rng.randint(1, 4) * 50} g {name}" for name in ingredients)
    instructions = "\n".join(rng.sample(STEPS, rng.randint(3, 5)))
    created_at = FIRST_DATE + timedelta(minutes=recipe_id * 7)
    recipe = (recipe_id, rng.choice(users), f"{title} #{recipe_id}", ingredient_text,
              instructions, created_at.strftime("%Y-%m-%d %H:%M:%S"))

    classes = [class_ids[("Taste", "Sweet" if sweet else "Savory")]]
    diet = rng.choice([None, "Keto", "LCHF"])
    if diet:
        classes.append(class_ids[("Diet", diet)])
    meal = rng.choice(meals)
    if meal:
        classes.append(class_ids[("Meal", meal)])
    for restriction in ["Dairy-free", "Egg-free", "Nut-free"]:
        if rng.random() < 0.25:
            classes.append(class_ids[("Restrictions", restriction)])
    return recipe, [(recipe_id, class_id) for class_id in classes]

def make_reviews(rng, recipes, users, count):
    reviews, reviewed = [], set()
    while len(reviews) < count:
        recipe_id, author_id, created_at = rng.choice(recipes)
        user_id = rng.choice(users)
        if user_id == author_id or (recipe_id, user_id) in reviewed:
            continue
        reviewed.add((recipe_id, user_id))
        rating = rng.choices([1, 2, 3, 4, 5], weights=[1, 2, 4, 6, 5])[0]
        date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        date += timedelta(hours=rng.randint(1, 24 * 30))
        reviews.append((recipe_id, user_id, rng.choice(REVIEWS), rating,
                        date.strftime("%Y-%m-%d %H:%M:%S")))
    return reviews

def generate_rows(args, class_ids):
    rng = random.Random(args.seed)

    # One hash for everybody: hashing is slow on purpose, and every user
    # still logs in with the same password.
    password_hash = generate_password_hash(PASSWORD)
    users = list(range(1, args.users + 1))
    user_rows = [(user_id, f"user{user_id:04d}", password_hash) for user_id in users]

    recipe_rows, class_rows = [], []
    for recipe_id in range(1, args.recipes + 1):
        recipe, classes = make_recipe(rng, recipe_id, users, class_ids)
        recipe_rows.append(recipe)
        class_rows.extend(classes)
    recipes = [(row[0], row[1], row[5]) for row in recipe_rows]
    review_rows = make_reviews(rng, recipes, users, args.reviews)
    return user_rows, recipe_rows, class_rows, review_rows

def insert_rows(con, user_rows, recipe_rows, class_rows, review_rows):
    # All rows are inserted in one transaction: much faster than one
    # commit per row, and nothing is saved if any insert fails.
    with con:
        con.executemany("INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                        user_rows)
        con.executemany("""INSERT INTO recipes (id, user_id, title, ingredients,
                                               instructions, created_at)
                           VALUES (?, ?, ?, ?, ?, ?)""", recipe_rows)
        con.executemany("INSERT INTO recipe_classes (recipe_id, class_id) VALUES (?, ?)",
                        class_rows)
        con.executemany("""INSERT INTO comments (recipe_id, user_id, content, rating,
                                                created_at)
                           VALUES (?, ?, ?, ?, ?)""", review_rows)

def print_summary(con, target):
    print(f"Created {target}")
    for table in ["users", "recipes", "recipe_classes", "comments"]:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count}")
    print("integrity_check:", con.execute("PRAGMA integrity_check").fetchone()[0])
    print("foreign_key_check:", con.execute("PRAGMA foreign_key_check").fetchall() or "ok")

def main():
    args = parse_arguments()
    target = check_target(args)

    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()

    con = sqlite3.connect(target)
    con.execute("PRAGMA foreign_keys = ON")
    for sql_file in SQL_FILES:
        con.executescript(sql_file.read_text(encoding="utf-8"))

    rows = generate_rows(args, get_class_ids(con))
    insert_rows(con, *rows)
    print_summary(con, target)
    con.close()

if __name__ == "__main__":
    main()
