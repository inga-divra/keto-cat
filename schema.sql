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
