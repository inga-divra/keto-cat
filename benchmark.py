"""Measure the user profile page with and without the idx_recipes_user index.

Usage:
    python seed.py --database test-data/large.db
    python benchmark.py --database test-data/large.db

The given database is only copied, never changed. Two temporary copies are
made: one without idx_recipes_user and one with it. Every round measures
all users' profile queries and profile pages in both copies in turn, and
the median of all measurements is reported.

db.py opens "database.db" from the current directory, so the Flask app is
pointed to a copy by changing to the copy's temporary folder.
"""
import argparse
import os
import platform
import shutil
import sqlite3
import statistics
import sys
import tempfile
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REAL_DATABASE = BASE_DIR / "database.db"
INDEX = "idx_recipes_user"
CREATE_INDEX = f"CREATE INDEX IF NOT EXISTS {INDEX} ON recipes (user_id)"

sys.path.insert(0, str(BASE_DIR))
import db  # noqa: E402
import users  # noqa: E402

def parse_arguments():
    parser = argparse.ArgumentParser(description="Benchmark the idx_recipes_user index.")
    parser.add_argument("--database", required=True, type=Path,
                        help="seeded test database (it is copied, not changed)")
    parser.add_argument("--rounds", type=int, default=15, help="measured rounds")
    parser.add_argument("--warmup", type=int, default=2, help="warm-up rounds")
    return parser.parse_args()

def check_source(path):
    source = path.resolve()
    if source == REAL_DATABASE.resolve() or source.name == "database.db":
        sys.exit("Refusing to use database.db: give a seeded test database.")
    if not source.is_file():
        sys.exit(f"{source} does not exist. Create it with seed.py first.")
    return source

def capture_sql(func, *args):
    """Return the SQL that an application function runs, without a database."""
    captured = []
    original = db.query
    db.query = lambda sql, params=(): captured.append(sql) or [[0]]
    try:
        func(*args)
    finally:
        db.query = original
    return captured[0]

QUERIES = {
    "users.get_recipe_count": capture_sql(users.get_recipe_count, 1),
    "users.get_recipes": capture_sql(users.get_recipes, 1),
}

def make_copies(source, folder):
    copies = {}
    for name, sql in [("without index", f"DROP INDEX IF EXISTS {INDEX}"),
                      ("with index", CREATE_INDEX)]:
        copy_folder = folder / name.replace(" ", "_")
        copy_folder.mkdir()
        shutil.copyfile(source, copy_folder / "database.db")
        con = sqlite3.connect(copy_folder / "database.db")
        con.execute(sql)
        con.commit()
        con.close()
        copies[name] = copy_folder
    return copies

def describe(path):
    con = sqlite3.connect(path)
    counts = {table: con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
              for table in ["users", "recipes", "recipe_classes", "comments"]}
    user_ids = [row[0] for row in con.execute("SELECT id FROM users ORDER BY id")]
    con.close()
    return counts, user_ids

def query_plans(path):
    con = sqlite3.connect(path)
    plans = {label: [row[3] for row in con.execute("EXPLAIN QUERY PLAN " + sql, [1])]
             for label, sql in QUERIES.items()}
    con.close()
    return plans

def load_client():
    try:
        from app import app  # pylint: disable=import-outside-toplevel
    except ImportError as error:
        print(f"Page timings skipped: the Flask app could not be imported ({error}).")
        return None
    return app.test_client()

def run_round(copies, connections, client, user_ids, samples):
    for name, folder in copies.items():
        con = connections[name]
        for label, sql in QUERIES.items():
            for user_id in user_ids:
                start = time.perf_counter()
                con.execute(sql, [user_id]).fetchall()
                samples[(label, name)].append(time.perf_counter() - start)
        if client is None:
            continue
        os.chdir(folder)
        # Safety check: the app must open the temporary copy.
        assert Path("database.db").resolve() != REAL_DATABASE.resolve()
        for user_id in user_ids:
            start = time.perf_counter()
            response = client.get(f"/user/{user_id}")
            elapsed = time.perf_counter() - start
            if response.status_code != 200:
                sys.exit(f"/user/{user_id} returned {response.status_code}")
            samples[("GET /user/<id>", name)].append(elapsed)

def main():
    args = parse_arguments()
    source = check_source(args.database)
    counts, user_ids = describe(source)
    print(f"Database: {source}")
    print("Rows: " + ", ".join(f"{table} {count}" for table, count in counts.items()))
    print(f"Python {platform.python_version()}, SQLite {sqlite3.sqlite_version}, "
          f"{platform.system()} {platform.release()}")
    print(f"{args.warmup} warm-up + {args.rounds} measured rounds, {len(user_ids)} users per round")
    print(f"Index: {CREATE_INDEX}")

    client = load_client()
    labels = list(QUERIES) + (["GET /user/<id>"] if client else [])
    start_dir = Path.cwd()
    with tempfile.TemporaryDirectory() as temp:
        copies = make_copies(source, Path(temp))
        connections = {}
        for name, folder in copies.items():
            con = sqlite3.connect(folder / "database.db")
            con.execute("PRAGMA foreign_keys = ON")
            con.row_factory = sqlite3.Row
            connections[name] = con
        try:
            warmup = {(label, name): [] for label in labels for name in copies}
            for _ in range(args.warmup):
                run_round(copies, connections, client, user_ids, warmup)
            samples = {(label, name): [] for label in labels for name in copies}
            for _ in range(args.rounds):
                run_round(copies, connections, client, user_ids, samples)
        finally:
            os.chdir(start_dir)
            for con in connections.values():
                con.close()

        for name, folder in copies.items():
            print(f"\nEXPLAIN QUERY PLAN, {name}:")
            for label, plan in query_plans(folder / "database.db").items():
                print(f"  {label}: " + " | ".join(plan))

    print(f"\n{'Measured':26}{'without index':>16}{'with index':>14}{'speedup':>10}")
    for label in labels:
        without = statistics.median(samples[(label, "without index")]) * 1000
        with_index = statistics.median(samples[(label, "with index")]) * 1000
        print(f"{label:26}{without:13.3f} ms{with_index:11.3f} ms{without / with_index:9.1f}x")
    print(f"(median of {len(samples[(labels[0], 'with index')])} measurements each)")

if __name__ == "__main__":
    main()
