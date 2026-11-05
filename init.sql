-- Classification options. INSERT OR IGNORE makes it safe to run this file
-- again on an existing database: options that already exist are skipped.
INSERT OR IGNORE INTO classes (title, value) VALUES ('Taste', 'Sweet');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Taste', 'Savory');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Diet', 'Keto');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Diet', 'LCHF');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Meal', 'Breakfast');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Meal', 'Main course');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Meal', 'Snack');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Meal', 'Dessert');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Restrictions', 'Dairy-free');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Restrictions', 'Egg-free');
INSERT OR IGNORE INTO classes (title, value) VALUES ('Restrictions', 'Nut-free');
