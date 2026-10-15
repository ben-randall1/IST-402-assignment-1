-- Proposed schema experiment for Assignment 3, not a migration of hotel data.
PRAGMA foreign_keys = ON;

CREATE TABLE skills (
    skill_id TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    title TEXT NOT NULL,
    steps_json TEXT NOT NULL CHECK (json_valid(steps_json)),
    enabled INTEGER NOT NULL DEFAULT 0 CHECK (enabled IN (0, 1)),
    PRIMARY KEY (skill_id, version)
);

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    skill_version INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    status TEXT NOT NULL CHECK (status IN ('ready', 'active', 'paused', 'completed', 'stopped', 'interrupted')),
    active_ms INTEGER NOT NULL DEFAULT 0 CHECK (active_ms >= 0),
    paused_ms INTEGER NOT NULL DEFAULT 0 CHECK (paused_ms >= 0),
    replay_ms INTEGER NOT NULL DEFAULT 0 CHECK (replay_ms >= 0),
    progress_json TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(progress_json)),
    revision INTEGER NOT NULL DEFAULT 0 CHECK (revision >= 0),
    FOREIGN KEY (skill_id, skill_version) REFERENCES skills(skill_id, version)
);

CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL CHECK (sequence >= 0),
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL CHECK (length(content) BETWEEN 1 AND 2000),
    source TEXT NOT NULL CHECK (source IN ('user', 'model', 'fallback')),
    model_id TEXT,
    response_code TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (session_id, sequence),
    CHECK ((role = 'user' AND source = 'user' AND model_id IS NULL)
        OR (role = 'assistant' AND source = 'fallback' AND model_id IS NULL)
        OR (role = 'assistant' AND source = 'model' AND model_id IS NOT NULL))
);

CREATE TABLE preferences (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    usual_skill_id TEXT NOT NULL,
    usual_skill_version INTEGER NOT NULL,
    source_session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
    chosen_at TEXT NOT NULL,
    FOREIGN KEY (usual_skill_id, usual_skill_version) REFERENCES skills(skill_id, version)
);

CREATE INDEX sessions_by_date ON sessions(started_at DESC, session_id);
CREATE INDEX messages_by_session ON messages(session_id, sequence);
