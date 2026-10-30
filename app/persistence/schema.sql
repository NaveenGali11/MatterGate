PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, name TEXT NOT NULL, role TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS policies (policy_version TEXT PRIMARY KEY, definition TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources (
 source_id TEXT PRIMARY KEY, title TEXT NOT NULL, classification TEXT NOT NULL,
 authority_tier TEXT NOT NULL, matter_id TEXT NOT NULL, version TEXT NOT NULL,
 allowed_actors TEXT NOT NULL, allowed_purposes TEXT NOT NULL, jurisdictions TEXT NOT NULL, url TEXT
);
CREATE TABLE IF NOT EXISTS source_chunks (
 chunk_id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES sources(source_id),
 text TEXT NOT NULL, content_hash TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(chunk_id UNINDEXED, text);
CREATE TABLE IF NOT EXISTS research_runs (
 run_id TEXT PRIMARY KEY, actor_id TEXT NOT NULL, matter_id TEXT NOT NULL,
 purpose TEXT NOT NULL, jurisdiction TEXT NOT NULL, mode TEXT NOT NULL,
 question TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
 scope_json TEXT, draft_json TEXT, provider_json TEXT, error_code TEXT
);
CREATE TABLE IF NOT EXISTS run_evidence (
 run_id TEXT NOT NULL REFERENCES research_runs(run_id), chunk_id TEXT NOT NULL REFERENCES source_chunks(chunk_id),
 PRIMARY KEY (run_id, chunk_id)
);
CREATE TABLE IF NOT EXISTS run_workspaces (
 run_id TEXT PRIMARY KEY REFERENCES research_runs(run_id), workspace_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS workspace_runs ON run_workspaces(workspace_id);
CREATE TABLE IF NOT EXISTS public_usage (
 period TEXT PRIMARY KEY, attempts INTEGER NOT NULL CHECK(attempts >= 0)
);
CREATE TABLE IF NOT EXISTS evaluation_results (
 run_id TEXT NOT NULL REFERENCES research_runs(run_id), check_id TEXT NOT NULL,
 passed INTEGER NOT NULL CHECK(passed IN (0,1)), reason TEXT NOT NULL,
 PRIMARY KEY (run_id, check_id)
);
CREATE TABLE IF NOT EXISTS review_decisions (
 review_id TEXT PRIMARY KEY, run_id TEXT NOT NULL UNIQUE REFERENCES research_runs(run_id),
 actor_id TEXT NOT NULL, decision TEXT NOT NULL, rationale TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS audit_events (
 event_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES research_runs(run_id),
 sequence_number INTEGER NOT NULL, event_type TEXT NOT NULL, created_at TEXT NOT NULL,
 actor_id TEXT, safe_payload_json TEXT NOT NULL, previous_event_hash TEXT NOT NULL, event_hash TEXT NOT NULL,
 UNIQUE (run_id, sequence_number)
);
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'immutable audit'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'immutable audit'); END;
CREATE TRIGGER IF NOT EXISTS reviews_no_update BEFORE UPDATE ON review_decisions BEGIN SELECT RAISE(ABORT, 'immutable review'); END;
CREATE TRIGGER IF NOT EXISTS reviews_no_delete BEFORE DELETE ON review_decisions BEGIN SELECT RAISE(ABORT, 'immutable review'); END;
