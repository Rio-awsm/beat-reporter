# db/sqlite.py
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from config import settings

def _connect() -> sqlite3.Connection:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def run_migrations():
    schema_dir = Path(__file__).parent / "schema"
    files = sorted(schema_dir.glob("*.sql"))
    with get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _migrations (name TEXT PRIMARY KEY, applied_at TEXT DEFAULT CURRENT_TIMESTAMP)"
        )
        applied = {row["name"] for row in conn.execute("SELECT name FROM _migrations")}
        for f in files:
            if f.name in applied:
                continue
            print(f"Applying migration: {f.name}")
            conn.executescript(f.read_text())
            conn.execute("INSERT INTO _migrations (name) VALUES (?)", (f.name,))