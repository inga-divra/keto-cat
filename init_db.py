"""Create database.db from schema.sql and init.sql.

Usage: python init_db.py
"""
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "database.db"
SQL_FILES = [BASE_DIR / "schema.sql", BASE_DIR / "init.sql"]

def main():
    if DATABASE.exists():
        answer = input(f"{DATABASE.name} already exists. "
                       "Delete it and create a new empty database? (yes/no): ")
        if answer.strip().lower() != "yes":
            print("Cancelled. The existing database was not changed.")
            return
        DATABASE.unlink()

    con = sqlite3.connect(DATABASE)
    for sql_file in SQL_FILES:
        con.executescript(sql_file.read_text(encoding="utf-8"))
    con.commit()
    con.close()
    print(f"Created {DATABASE.name}")

if __name__ == "__main__":
    main()
