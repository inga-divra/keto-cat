from werkzeug.security import check_password_hash, generate_password_hash
import db

def create_user(username, password):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    sql = "SELECT id, username, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user = result[0]
    if check_password_hash(user["password_hash"], password):
        return user
    return None

def get_user(user_id):
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_recipe_count(user_id):
    sql = "SELECT COUNT(*) FROM recipes WHERE user_id = ?"
    return db.query(sql, [user_id])[0][0]

def get_recipes(user_id):
    # LEFT JOIN keeps recipes that have no taste selected yet.
    sql = """SELECT recipes.id, recipes.title, recipes.created_at,
                    taste.value AS taste
             FROM recipes
                  LEFT JOIN recipe_classes
                       ON recipe_classes.recipe_id = recipes.id
                       AND recipe_classes.class_id IN
                           (SELECT id FROM classes WHERE title = 'Taste')
                  LEFT JOIN classes AS taste ON taste.id = recipe_classes.class_id
             WHERE recipes.user_id = ?
             ORDER BY recipes.id DESC"""
    return db.query(sql, [user_id])

def get_comment_count(user_id):
    sql = "SELECT COUNT(*) FROM comments WHERE user_id = ?"
    return db.query(sql, [user_id])[0][0]
