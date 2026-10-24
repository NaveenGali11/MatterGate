import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from uuid import uuid4

from app.config import ROOT
from app.domain import ControlError, Status, TRANSITIONS, now

SAFE_FIELDS = {"status", "reason_code", "policy_decision", "policy_version", "source_ids", "chunk_ids", "mode", "provider", "model_id", "request_id", "latency_ms", "checks", "decision", "prompt_hash", "prompt_version", "fixture_version", "fixture_hash", "count", "attempt", "note_code"}


def canonical(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def event_hash(event):
    body = {key: value for key, value in event.items() if key != "event_hash"}
    return hashlib.sha256(canonical(body).encode()).hexdigest()


class Database:
    def __init__(self, path):
        if path != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self.connection = sqlite3.connect(path, check_same_thread=False, timeout=5)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript((ROOT / "persistence/schema.sql").read_text())

    @contextmanager
    def transaction(self):
        with self.lock, self.connection:
            yield self.connection

    def rows(self, sql, values=()):
        with self.lock:
            return [dict(row) for row in self.connection.execute(sql, values).fetchall()]

    def one(self, sql, values=()):
        rows = self.rows(sql, values)
        return rows[0] if rows else None

    def append_event(self, cx, run_id, event_type, payload=None, actor_id=None):
        payload = payload or {}
        if set(payload) - SAFE_FIELDS:
            raise ControlError("UNSAFE_AUDIT_PAYLOAD")
        previous = cx.execute("SELECT sequence_number,event_hash FROM audit_events WHERE run_id=? ORDER BY sequence_number DESC LIMIT 1", (run_id,)).fetchone()
        event = dict(event_id=str(uuid4()), run_id=run_id, sequence_number=1 if previous is None else previous[0]+1,
                     event_type=event_type, created_at=now(), actor_id=actor_id,
                     safe_payload_json=canonical(payload), previous_event_hash="0"*64 if previous is None else previous[1])
        event["event_hash"] = event_hash(event)
        cx.execute("INSERT INTO audit_events VALUES (?,?,?,?,?,?,?,?,?)", tuple(event.values()))

    def transition(self, run_id, target, event_type, payload=None, **fields):
        if set(fields) - {"scope_json", "draft_json", "provider_json", "error_code", "question"}:
            raise ControlError("INVALID_RUN_FIELDS")
        with self.transaction() as cx:
            row = cx.execute("SELECT status FROM research_runs WHERE run_id=?", (run_id,)).fetchone()
            if row is None or target not in TRANSITIONS.get(Status(row[0]), set()):
                raise ControlError("INVALID_TRANSITION")
            updates = {"status": str(target), **fields}
            cx.execute("UPDATE research_runs SET "+",".join(f"{key}=?" for key in updates)+" WHERE run_id=?", (*updates.values(), run_id))
            self.append_event(cx, run_id, event_type, {"status": str(target), **(payload or {})})

    def verify_chain(self, run_id):
        previous = "0"*64
        for index, event in enumerate(self.rows("SELECT * FROM audit_events WHERE run_id=? ORDER BY sequence_number", (run_id,)), 1):
            if event["sequence_number"] != index or event["previous_event_hash"] != previous or event["event_hash"] != event_hash(event):
                return False
            previous = event["event_hash"]
        return True

    def close(self):
        self.connection.close()
