import db

def add_recipe(user_id, title, ingredients, instructions):
    sql = """INSERT INTO recipes (user_id, title, ingredients, instructions)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [user_id, title, ingredients, instructions])
    return db.last_insert_id()

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

def update_recipe(recipe_id, title, ingredients, instructions):
    sql = """UPDATE recipes SET title = ?, ingredients = ?, instructions = ?
             WHERE id = ?"""
    db.execute(sql, [title, ingredients, instructions, recipe_id])

def remove_recipe(recipe_id):
    sql = "DELETE FROM recipes WHERE id = ?"
    db.execute(sql, [recipe_id])
