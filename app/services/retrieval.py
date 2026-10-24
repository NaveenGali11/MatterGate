"""SQL portions adapted from PriviLAB sqlite_fts.py, Apache-2.0.
Copyright 2026 Data Strategy Lab LLC. Modified: MatterGate source allowlist,
purpose/jurisdiction checks, schema and bounded context. Keeps local match-density
ranking to avoid corpus-wide BM25 statistics influencing scoped ordering.
Upstream: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
import re
import hashlib

from app.domain import AccessScope, ControlError, Evidence


def retrieve(db, question: str, scope: AccessScope):
    if not isinstance(scope, AccessScope):
        raise ControlError("SCOPE_REQUIRED")
    scope.require_allow()
    tokens = list(dict.fromkeys(re.findall(r"[\w]{3,}", question.lower())))[:40]
    if not tokens:
        return []
    query = " OR ".join('"'+token.replace('"','""')+'"' for token in tokens)
    placeholders = ",".join("?" for _ in scope.allowed_source_ids)
    rows = db.rows(f"""
      WITH authorized_sources AS (
        SELECT * FROM sources WHERE source_id IN ({placeholders})
        AND classification != 'RESTRICTED_PRIVILEGED' AND matter_id IN (?, 'all')
        AND EXISTS(SELECT 1 FROM json_each(allowed_actors) WHERE value=?)
        AND EXISTS(SELECT 1 FROM json_each(allowed_purposes) WHERE value=?)
        AND EXISTS(SELECT 1 FROM json_each(jurisdictions) WHERE value=?)
      ), authorized_chunks AS (
        SELECT c.* FROM source_chunks c JOIN authorized_sources s USING(source_id)
      ), authorized_matches AS (
        SELECT c.chunk_id, c.source_id, c.text, c.content_hash,
          (length(highlight(chunks_fts,1,char(1),char(2)))-length(c.text))/2.0/length(c.text) AS score
        FROM chunks_fts JOIN authorized_chunks c ON c.chunk_id=chunks_fts.chunk_id
        WHERE chunks_fts MATCH ?
      )
      SELECT c.chunk_id,c.source_id,c.text,c.content_hash,s.title,s.classification,
             s.authority_tier,s.matter_id,s.version,s.url
      FROM authorized_matches c JOIN authorized_sources s USING(source_id)
      ORDER BY c.score DESC,c.source_id,c.chunk_id LIMIT 5
    """, (*scope.allowed_source_ids, scope.matter_id, scope.actor_id, scope.purpose, scope.jurisdiction, query))
    selected, size = [], 0
    for row in rows:
        if hashlib.sha256(row["text"].encode()).hexdigest() != row["content_hash"]:
            raise ControlError("EVIDENCE_INTEGRITY_FAILED")
        if size+len(row["text"]) > 8000:
            continue
        selected.append(Evidence.model_validate(row))
        size += len(row["text"])
    return selected
