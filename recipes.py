import db

def get_classes(title):
    sql = "SELECT id, value FROM classes WHERE title = ? ORDER BY id"
    return db.query(sql, [title])

def get_class(title, value):
    sql = "SELECT id, value FROM classes WHERE title = ? AND value = ?"
    result = db.query(sql, [title, value])
    return result[0] if result else None

def get_recipe_classes(recipe_id):
    sql = """SELECT classes.id, classes.title, classes.value
             FROM classes, recipe_classes
             WHERE recipe_classes.class_id = classes.id
                   AND recipe_classes.recipe_id = ?
             ORDER BY classes.id"""
    return db.query(sql, [recipe_id])

def add_recipe_classes(recipe_id, class_ids):
    sql = "INSERT INTO recipe_classes (recipe_id, class_id) VALUES (?, ?)"
    for class_id in class_ids:
        db.execute(sql, [recipe_id, class_id])

def add_recipe(user_id, title, ingredients, instructions, class_ids):
    sql = """INSERT INTO recipes (user_id, title, ingredients, instructions)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, ingredients, instructions])
    recipe_id = db.last_insert_id()
    add_recipe_classes(recipe_id, class_ids)
    return recipe_id

def get_recipes():
    sql = """SELECT recipes.id, recipes.title, recipes.created_at,
                    users.id AS user_id, users.username
             FROM recipes, users
             WHERE recipes.user_id = users.id
             ORDER BY recipes.id DESC"""
    return db.query(sql)

def get_recipe(recipe_id):
    sql = """SELECT recipes.id, recipes.title, recipes.ingredients,
                    recipes.instructions, recipes.created_at,
                    users.id AS user_id, users.username
             FROM recipes, users
             WHERE recipes.user_id = users.id AND recipes.id = ?"""
    result = db.query(sql, [recipe_id])
    return result[0] if result else None

def get_random_recipe(class_id, exclude_id=0):
    sql = """SELECT recipes.id, recipes.title, users.username
             FROM recipes, users, recipe_classes
             WHERE recipes.user_id = users.id
                   AND recipe_classes.recipe_id = recipes.id
                   AND recipe_classes.class_id = ?
                   AND recipes.id != ?
             ORDER BY RANDOM()
             LIMIT 1"""
    result = db.query(sql, [class_id, exclude_id])
    return result[0] if result else None

def update_recipe(recipe_id, title, ingredients, instructions, class_ids):
    sql = """UPDATE recipes SET title = ?, ingredients = ?, instructions = ?
             WHERE id = ?"""
    db.execute(sql, [title, ingredients, instructions, recipe_id])

    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    add_recipe_classes(recipe_id, class_ids)

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipe_classes WHERE recipe_id = ?"
    db.execute(sql, [recipe_id])
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])
