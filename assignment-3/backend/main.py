"""A little space — fictional-scenario localhost coursework API."""
import json
import sqlite3
from contextlib import asynccontextmanager
from typing import Literal
from uuid import UUID, uuid4, uuid5, NAMESPACE_URL

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import storage
from domain import SKILL, RESPONSES, CRISIS_COPY, crisis_match
from provider import OpenRouter, ModelError

model = OpenRouter()


@asynccontextmanager
async def lifespan(app):
    storage.initialize()
    yield


app = FastAPI(title="A little space · coursework prototype", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"], allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"], allow_headers=["Content-Type"])


@app.exception_handler(sqlite3.Error)
async def storage_failure(request, error):
    return JSONResponse(status_code=503, content={"detail": "Local history could not be saved or read. The practice and crisis information remain available."})


class NewSession(BaseModel):
    session_id: UUID


class SessionUpdate(BaseModel):
    expected_revision: int = Field(ge=0)
    status: Literal["ready", "active", "paused", "completed", "stopped", "interrupted"]
    active_ms: int = Field(ge=0, le=86400000)
    paused_ms: int = Field(ge=0, le=86400000)
    replay_ms: int = Field(ge=0, le=86400000)
    progress: dict = Field(default_factory=dict)


class NewMessage(BaseModel):
    request_id: UUID
    expected_revision: int = Field(ge=0)
    text: str = Field(min_length=1, max_length=500)


class UsualChoice(BaseModel):
    source_session_id: UUID


def require_session(db, session_id):
    row = storage.get_session(db, str(session_id))
    if row is None:
        raise HTTPException(404, "That local session no longer exists.")
    return row


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": model.mode, "model_configured": model.configured, "live_calls": model.calls, "limit": 50}


@app.get("/api/skills")
def skills():
    return {"skills": [SKILL], "coursework_only": True}


@app.post("/api/sessions", status_code=201)
def create_session(payload: NewSession):
    with storage.connection() as db:
        db.execute("INSERT OR IGNORE INTO sessions(session_id,skill_id,skill_version,started_at,status) VALUES (?, ?, ?, ?, 'ready')", (str(payload.session_id), SKILL["skill_id"], SKILL["version"], storage.utc_now()))
        return storage.session_dict(require_session(db, payload.session_id))


@app.get("/api/sessions")
def list_sessions(limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0)):
    with storage.connection() as db:
        rows = db.execute("SELECT s.*, (SELECT COUNT(*) FROM messages m WHERE m.session_id=s.session_id) AS message_count FROM sessions s ORDER BY started_at DESC,session_id LIMIT ? OFFSET ?", (limit, offset)).fetchall()
        return {"sessions": [storage.session_dict(row) for row in rows], "limit": limit, "offset": offset, "total": db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]}


@app.get("/api/sessions/{session_id}")
def read_session(session_id: UUID):
    with storage.connection() as db:
        return {"session": storage.session_dict(require_session(db, session_id)), "messages": storage.messages(db, str(session_id)), "attempts": [dict(row) for row in db.execute("SELECT a.* FROM message_attempts a JOIN messages m ON m.message_id=a.user_message_id WHERE m.session_id=? ORDER BY m.sequence", (str(session_id),))]}


@app.patch("/api/sessions/{session_id}")
def update_session(session_id: UUID, payload: SessionUpdate):
    if len(json.dumps(payload.progress)) > 4000:
        raise HTTPException(422, "Progress snapshot is too large.")
    allowed = {"ready": {"ready", "active", "stopped", "interrupted"}, "active": {"active", "paused", "completed", "stopped", "interrupted"}, "paused": {"paused", "active", "stopped", "interrupted"}, "completed": {"completed"}, "stopped": {"stopped"}, "interrupted": {"interrupted"}}
    with storage.connection() as db:
        row = require_session(db, session_id)
        if row["revision"] != payload.expected_revision:
            raise HTTPException(409, "The session changed. Review its saved history before trying again.")
        if payload.status not in allowed[row["status"]]:
            raise HTTPException(409, "That session cannot change to the requested state.")
        if payload.active_ms < row["active_ms"] or payload.paused_ms < row["paused_ms"] or payload.replay_ms < row["replay_ms"]:
            raise HTTPException(422, "Recorded elapsed times cannot move backwards.")
        if payload.status == "completed" and payload.active_ms < 60000:
            raise HTTPException(422, "The planned breathing sequence has not ended.")
        ended_at = storage.utc_now() if payload.status in {"completed", "stopped", "interrupted"} else None
        result = db.execute("UPDATE sessions SET status=?,active_ms=?,paused_ms=?,replay_ms=?,progress_json=?,ended_at=?,revision=revision+1 WHERE session_id=? AND revision=?", (payload.status, payload.active_ms, payload.paused_ms, payload.replay_ms, json.dumps(payload.progress), ended_at, str(session_id), payload.expected_revision))
        if result.rowcount != 1:
            raise HTTPException(409, "The session changed. Please refresh its history.")
        return storage.session_dict(require_session(db, session_id))


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: UUID):
    with storage.connection() as db:
        require_session(db, session_id)
        db.execute("DELETE FROM sessions WHERE session_id=?", (str(session_id),))
    return {"deleted": True}


@app.get("/api/preferences/usual")
def get_usual():
    with storage.connection() as db:
        return {"usual": storage.usual(db)}


@app.put("/api/preferences/usual")
def set_usual(payload: UsualChoice):
    with storage.connection() as db:
        row = require_session(db, payload.source_session_id)
        db.execute("INSERT INTO preferences VALUES (1, ?, ?, ?, ?) ON CONFLICT(singleton) DO UPDATE SET usual_skill_id=excluded.usual_skill_id,usual_skill_version=excluded.usual_skill_version,source_session_id=excluded.source_session_id,chosen_at=excluded.chosen_at", (row["skill_id"], row["skill_version"], str(payload.source_session_id), storage.utc_now()))
        return {"usual": storage.usual(db)}


@app.delete("/api/preferences/usual")
def clear_usual():
    with storage.connection() as db:
        db.execute("DELETE FROM preferences")
    return {"usual": None}


@app.post("/api/sessions/{session_id}/messages")
def send_message(session_id: UUID, payload: NewMessage):
    text = payload.text.strip()
    if not text:
        raise HTTPException(422, "Enter a fictional message, or skip to the practice.")
    session_id, request_id = str(session_id), str(payload.request_id)
    with storage.connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = require_session(db, session_id)
        previous = db.execute("SELECT a.* FROM message_attempts a JOIN messages m ON m.message_id=a.user_message_id WHERE a.user_message_id=? AND m.session_id=?", (request_id, session_id)).fetchone()
        if previous:
            if previous["status"] == "succeeded":
                return {"session": storage.session_dict(row), "messages": storage.messages(db, session_id), "crisis": previous["response_id"] == "crisis", "response_id": previous["response_id"], "idempotent": True}
            raise HTTPException(409, "That message was already attempted. It will not make another model request. Send again explicitly if needed.")
        if row["revision"] != payload.expected_revision or row["status"] != "ready":
            raise HTTPException(409, "Messages are available before practice starts. The session changed; this response cannot replace the current screen.")
        count = db.execute("SELECT COUNT(*) FROM messages WHERE session_id=?", (session_id,)).fetchone()[0]
        if count >= 100:
            raise HTTPException(429, "This session's conversation limit was reached. You can still start or leave the practice.")
        history = storage.messages(db, session_id)[-4:]
        context = {"question": text, "skill": SKILL, "allowed_responses": RESPONSES, "explicit_preference": storage.usual(db), "history": [{"role": m["role"], "content": m["content"][:500]} for m in history]}
        sequence = db.execute("SELECT COALESCE(MAX(sequence),-1)+1 FROM messages WHERE session_id=?", (session_id,)).fetchone()[0]
        db.execute("INSERT INTO messages VALUES (?, ?, ?, 'user', ?, 'user', NULL, NULL, ?)", (request_id, session_id, sequence, text, storage.utc_now()))
        db.execute("INSERT INTO message_attempts(user_message_id,status) VALUES (?, 'pending')", (request_id,))
        db.execute("UPDATE sessions SET revision=revision+1 WHERE session_id=?", (session_id,))
        expected_revision = row["revision"] + 1
    crisis = crisis_match(text)
    try:
        if crisis:
            proposal, model_id, source = {"response_id": "crisis", "suggested_skill_id": None}, None, "fallback"
        else:
            proposal, model_id = model.select(context)
            source = "model" if model.mode == "live" else "fallback"
    except ModelError as error:
        with storage.connection() as db:
            db.execute("UPDATE message_attempts SET status='failed', error_status=? WHERE user_message_id=?", (error.status, request_id))
        raise HTTPException(error.status, str(error), headers={"Retry-After": "60"} if error.status == 429 else None) from None
    with storage.connection() as db:
        db.execute("BEGIN IMMEDIATE")
        row = require_session(db, session_id)
        if row["revision"] != expected_revision or row["status"] != "ready":
            db.execute("UPDATE message_attempts SET status='stale' WHERE user_message_id=?", (request_id,))
            # Commit the stale marker before returning the conflict.
            db.commit()
            raise HTTPException(409, "The session changed while the message was loading. The late reply was not displayed or saved as an answer.")
        code = proposal["response_id"]
        content = CRISIS_COPY if crisis else RESPONSES[code]
        if model.mode != "live" and not crisis:
            content = "[MOCK RESPONSE] " + content
        sequence = db.execute("SELECT COALESCE(MAX(sequence),-1)+1 FROM messages WHERE session_id=?", (session_id,)).fetchone()[0]
        db.execute("INSERT INTO messages VALUES (?, ?, ?, 'assistant', ?, ?, ?, ?, ?)", (str(uuid5(NAMESPACE_URL, request_id + ":reply")), session_id, sequence, content, source, model_id if source == "model" else None, code, storage.utc_now()))
        db.execute("UPDATE message_attempts SET status='succeeded', response_id=?, suggested_skill_id=? WHERE user_message_id=?", (code, proposal["suggested_skill_id"], request_id))
        db.execute("UPDATE sessions SET revision=revision+1 WHERE session_id=?", (session_id,))
        return {"session": storage.session_dict(require_session(db, session_id)), "messages": storage.messages(db, session_id), "crisis": crisis, "response_id": code, "proposal": proposal, "context_record_count": len(history), "mode": model.mode}
