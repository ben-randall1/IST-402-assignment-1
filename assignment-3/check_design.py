"""Check design artifacts and a proposed schema in isolation; no app/runtime claims."""
from __future__ import annotations

import json
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise AssertionError(message)
    print("PASS:", message)


def expect_integrity(connection, sql, parameters=()):
    try:
        connection.execute(sql, parameters)
    except sqlite3.IntegrityError:
        return True
    raise AssertionError("Expected schema constraint rejection")


def main():
    print("Assignment 3.1 design/schema experiment")
    print("Observed UTC:", datetime.now(timezone.utc).isoformat())
    print("Scope: static artifacts, temporary SQLite and timing arithmetic; no runtime skill or live model.")
    for name in ["README.md", "AGENTS.md", "research.md", "design.md", "technical-design.md", "verification.md", "evidence/process.md"]:
        path = ROOT / name
        check(path.is_file(), f"required artifact exists: {name}")
        for href in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if re.match(r"(?:https?:|tel:|sms:|#)", href):
                continue
            target = href.split("#", 1)[0]
            check((path.parent / target).exists(), f"local link resolves: {name} -> {target}")
    ElementTree.parse(ROOT / "storyboard.svg")
    check(True, "storyboard is valid SVG/XML")
    design = (ROOT / "design.md").read_text()
    check(all(code in design for code in ["R1", "R2", "R3", "R4", "D1", "D2", "D3", "D4", "D5", "D6"]), "all ten study codes have design traceability")
    prototype = (ROOT / "prototype.html").read_text()
    check(not re.search(r"\b(fetch|XMLHttpRequest|localStorage|sessionStorage)\b|<script[^>]+src=", prototype), "walkthrough has no remote model or persistent-storage implementation")
    check('id="support-open"' in prototype and 'data-inert' in prototype, "walkthrough has independent support panel and inert contact controls")
    durations = [duration for _ in range(6) for duration in (4000, 6000)]
    check(sum(durations) == 60000, "planned 4–6 sequence is six cycles / 60 seconds, not a measured runtime")
    with tempfile.TemporaryDirectory(prefix="assignment3-schema-") as directory:
        database = Path(directory) / "fictional.db"
        connection = sqlite3.connect(database)
        connection.executescript((ROOT / "schema.sql").read_text())
        check(connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign keys enabled in schema experiment")
        connection.execute("INSERT INTO skills VALUES (?, ?, ?, ?, ?)", ("breathing-4-6", 1, "Paced breathing", json.dumps([{"inhale": 4, "exhale": 6, "cycles": 6}]), 1))
        connection.execute("INSERT INTO sessions(session_id,skill_id,skill_version,started_at,status) VALUES ('fictional-session','breathing-4-6',1,'2026-10-15T18:00:00Z','ready')")
        connection.execute("INSERT INTO messages VALUES ('message-1','fictional-session',0,'user','Fictional: what do four and six mean?','user',NULL,NULL,'2026-10-15T18:00:01Z')")
        connection.execute("INSERT INTO messages VALUES ('message-2','fictional-session',1,'assistant','The screen carries the pace.','model','MOCK-fixture','explain_breathing','2026-10-15T18:00:02Z')")
        connection.execute("INSERT INTO preferences VALUES (1,'breathing-4-6',1,'fictional-session','2026-10-15T18:00:03Z')")
        check(expect_integrity(connection, "INSERT INTO preferences VALUES (2,'breathing-4-6',1,'fictional-session','test')"), "usual preference cannot have multiple singleton IDs")
        check(expect_integrity(connection, "INSERT INTO sessions(session_id,skill_id,skill_version,started_at,status) VALUES ('bad','unknown',1,'test','ready')"), "session cannot refer to unknown skill")
        check(expect_integrity(connection, "UPDATE sessions SET status='failed-person'"), "session status rejects unrecognized labels")
        check(expect_integrity(connection, "INSERT INTO messages VALUES ('duplicate','fictional-session',1,'user','Fictional duplicate','user',NULL,NULL,'test')"), "session message sequence is unique")
        check(expect_integrity(connection, "UPDATE messages SET source='model' WHERE role='user'"), "message source cannot mislabel user input as model output")
        connection.commit()
        connection.close()
        connection = sqlite3.connect(database)
        connection.execute("PRAGMA foreign_keys=ON")
        check(connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] == 1 and connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 2, "fictional session/conversation survive reopening SQLite file")
        check(connection.execute("SELECT usual_skill_id FROM preferences").fetchone()[0] == "breathing-4-6", "explicit fictional usual choice survives reopening")
        connection.execute("DELETE FROM sessions WHERE session_id='fictional-session'")
        check(connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0] == 0 and connection.execute("SELECT COUNT(*) FROM preferences").fetchone()[0] == 0, "deleting source session cascades to messages and usual choice")
        check(connection.execute("SELECT COUNT(*) FROM skills").fetchone()[0] == 1, "history deletion preserves fixed skill content")
        connection.close()
    print("COMPLETE: design/schema checks only. Browser observations are recorded separately.")


if __name__ == "__main__":
    main()
