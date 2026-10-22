"""SQLite persistence independent of all hotel tables. Parameterized queries only."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from domain import SKILL

APP_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = APP_ROOT / "data" / "skills.db"


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection():
    db = sqlite3.connect(DATABASE_PATH, timeout=5)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        with db:
            yield db
    finally:
        db.close()


def initialize():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = (APP_ROOT / "schema.sql").read_text().replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ").replace("CREATE INDEX ", "CREATE INDEX IF NOT EXISTS ")
    with connection() as db:
        db.executescript(schema)
        db.executescript("""CREATE TABLE IF NOT EXISTS message_attempts (
            user_message_id TEXT PRIMARY KEY REFERENCES messages(message_id) ON DELETE CASCADE,
            status TEXT NOT NULL CHECK(status IN ('pending','succeeded','failed','stale')),
            error_status INTEGER,
            response_id TEXT,
            suggested_skill_id TEXT
        );""")
        db.execute("INSERT OR IGNORE INTO skills VALUES (?, ?, ?, ?, 1)", (SKILL["skill_id"], SKILL["version"], SKILL["title"], json.dumps(SKILL)))
        db.execute("UPDATE sessions SET status='interrupted', ended_at=?, revision=revision+1 WHERE status='active'", (utc_now(),))
        db.execute("UPDATE message_attempts SET status='failed', error_status=503 WHERE status='pending'")


def session_dict(row):
    result = dict(row)
    result["progress"] = json.loads(result.pop("progress_json"))
    return result


def get_session(db, session_id):
    return db.execute("SELECT * FROM sessions WHERE session_id=?", (session_id,)).fetchone()


def messages(db, session_id):
    return [dict(row) for row in db.execute("SELECT * FROM messages WHERE session_id=? ORDER BY sequence", (session_id,))]


def usual(db):
    row = db.execute("SELECT * FROM preferences WHERE singleton=1").fetchone()
    return dict(row) if row else None
