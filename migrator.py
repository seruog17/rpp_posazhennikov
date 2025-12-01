import os
import psycopg2
import yaml

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://sub_user:sub_pass@localhost:5432/subscriptions_db")

def run_migrations():
    with open("changelog.yaml") as f:
        changelog = yaml.safe_load(f)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS migrations_log (
    id SERIAL PRIMARY KEY,
    migration_id INT NOT NULL,
    file_path TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id SERIAL PRIMARY KEY,
        user_id INT REFERENCES users(id),
        name TEXT NOT NULL,
        amount NUMERIC NOT NULL,
        period TEXT NOT NULL,
        start_date DATE NOT NULL,
        next_payment DATE NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id SERIAL PRIMARY KEY,
        subscription_id INT,
        action TEXT,
        action_date TIMESTAMP
    );
    """)
    conn.commit()

    for migration in changelog:
        cur.execute("SELECT * FROM migrations_log WHERE migration_id=%s", (migration["id"],))
        if not cur.fetchone():
            with open(migration["file_path"], "r") as sql_file:
                sql = sql_file.read()
                cur.execute(sql)
            cur.execute("INSERT INTO migrations_log (migration_id, file_path) VALUES (%s, %s)",
                        (migration["id"], migration["file_path"]))
            conn.commit()
    cur.close()
    conn.close()
