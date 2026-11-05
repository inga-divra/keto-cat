CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,
    instructions TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    value TEXT NOT NULL,
    UNIQUE (title, value)
);

CREATE TABLE IF NOT EXISTS recipe_classes (
    recipe_id INTEGER NOT NULL REFERENCES recipes(id),
    class_id INTEGER NOT NULL REFERENCES classes(id),
    PRIMARY KEY (recipe_id, class_id)
);

-- Reviews: one comment with a 1-5 rating per user and recipe.
-- ON DELETE CASCADE removes the reviews of a deleted recipe
-- (db.py turns on foreign key enforcement for every connection).
CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (recipe_id, user_id)
);
