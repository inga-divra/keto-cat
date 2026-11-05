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

def get_all_classes():
    sql = "SELECT id, title, value FROM classes ORDER BY id"
    return db.query(sql)

# A recipe and its classes are saved with one connection and one commit:
# if any statement fails, the connection is closed without commit and
# nothing is saved, so a recipe cannot be left with half of its classes.

def add_recipe_classes(con, recipe_id, class_ids):
    sql = "INSERT INTO recipe_classes (recipe_id, class_id) VALUES (?, ?)"
    for class_id in class_ids:
        con.execute(sql, [recipe_id, class_id])

def add_recipe(user_id, title, ingredients, instructions, class_ids):
    con = db.get_connection()
    try:
        sql = """INSERT INTO recipes (user_id, title, ingredients, instructions)
                 VALUES (?, ?, ?, ?)"""
        recipe_id = con.execute(sql, [user_id, title, ingredients, instructions]).lastrowid
        add_recipe_classes(con, recipe_id, class_ids)
        con.commit()
    finally:
        con.close()
    return recipe_id

def search_conditions(keyword, taste_id):
    # The FROM and WHERE part shared by get_recipes and recipe_count,
    # so that the page and the total count always use the same search.

    # Escape LIKE wildcards so that "%" and "_" in the keyword match literally.
    keyword = keyword.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    like = "%" + keyword + "%"

    # LEFT JOIN keeps recipes that have no taste selected yet. Only Taste
    # classes are joined, so each recipe gives exactly one row.
    sql = """FROM recipes
                  JOIN users ON users.id = recipes.user_id
                  LEFT JOIN recipe_classes
                       ON recipe_classes.recipe_id = recipes.id
                       AND recipe_classes.class_id IN
                           (SELECT id FROM classes WHERE title = 'Taste')
                  LEFT JOIN classes AS taste ON taste.id = recipe_classes.class_id
             WHERE (recipes.title LIKE ? ESCAPE '\\'
                    OR recipes.ingredients LIKE ? ESCAPE '\\')"""
    params = [like, like]

    if taste_id:
        sql += " AND taste.id = ?"
        params.append(taste_id)
    return sql, params

def recipe_count(keyword="", taste_id=None):
    conditions, params = search_conditions(keyword, taste_id)
    return db.query("SELECT COUNT(*) " + conditions, params)[0][0]

def get_recipes(keyword="", taste_id=None, page=1, page_size=10):
    conditions, params = search_conditions(keyword, taste_id)
    sql = """SELECT recipes.id, recipes.title, recipes.created_at,
                    users.id AS user_id, users.username,
                    taste.value AS taste
             """ + conditions + """
             ORDER BY recipes.id DESC
             LIMIT ? OFFSET ?"""
    return db.query(sql, params + [page_size, page_size * (page - 1)])

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
    con = db.get_connection()
    try:
        sql = """UPDATE recipes SET title = ?, ingredients = ?, instructions = ?
                 WHERE id = ?"""
        con.execute(sql, [title, ingredients, instructions, recipe_id])
        con.execute("DELETE FROM recipe_classes WHERE recipe_id = ?", [recipe_id])
        add_recipe_classes(con, recipe_id, class_ids)
        con.commit()
    finally:
        con.close()

def remove_recipe(recipe_id):
    # The reviews are removed too: explicitly here, and by ON DELETE CASCADE
    # in schema.sql as a safety net.
    con = db.get_connection()
    try:
        con.execute("DELETE FROM comments WHERE recipe_id = ?", [recipe_id])
        con.execute("DELETE FROM recipe_classes WHERE recipe_id = ?", [recipe_id])
        con.execute("DELETE FROM recipes WHERE id = ?", [recipe_id])
        con.commit()
    finally:
        con.close()

def get_comments(recipe_id):
    sql = """SELECT comments.id, comments.content, comments.rating,
                    comments.created_at, users.id AS user_id, users.username
             FROM comments, users
             WHERE comments.user_id = users.id AND comments.recipe_id = ?
             ORDER BY comments.id DESC"""
    return db.query(sql, [recipe_id])

def get_rating(recipe_id):
    sql = """SELECT COUNT(*) AS count, ROUND(AVG(rating), 1) AS average
             FROM comments
             WHERE recipe_id = ?"""
    return db.query(sql, [recipe_id])[0]

def get_comment(comment_id):
    sql = """SELECT comments.id, comments.content, comments.rating,
                    comments.user_id, comments.recipe_id,
                    recipes.title AS recipe_title
             FROM comments, recipes
             WHERE comments.recipe_id = recipes.id AND comments.id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def has_comment(recipe_id, user_id):
    sql = "SELECT id FROM comments WHERE recipe_id = ? AND user_id = ?"
    return bool(db.query(sql, [recipe_id, user_id]))

def add_comment(recipe_id, user_id, content, rating):
    sql = """INSERT INTO comments (recipe_id, user_id, content, rating)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [recipe_id, user_id, content, rating])

def update_comment(comment_id, content, rating):
    sql = "UPDATE comments SET content = ?, rating = ? WHERE id = ?"
    db.execute(sql, [content, rating, comment_id])

def remove_comment(comment_id):
    sql = "DELETE FROM comments WHERE id = ?"
    db.execute(sql, [comment_id])
