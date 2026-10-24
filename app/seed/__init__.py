"""Synthetic demo records and an attributed public-reference paraphrase."""
import hashlib
import json

from app.config import ROOT
from app.domain import POLICY_VERSION

USERS = {
    "jordan_sales_ops": {"name": "Jordan", "role": "Sales Operations", "initials": "JO"},
    "maya_privacy_counsel": {"name": "Maya", "role": "Privacy Counsel", "initials": "MA"},
    "alex_reviewer": {"name": "Alex", "role": "Human Reviewer", "initials": "AL"},
}


def seed(db):
    corpus = json.loads((ROOT / "seed/sources.json").read_text())
    policy = json.loads((ROOT / "seed/policy.json").read_text())
    with db.transaction() as cx:
        cx.executemany("INSERT OR IGNORE INTO users VALUES (?,?,?)", [(uid, value["name"], value["role"]) for uid, value in USERS.items()])
        cx.execute("INSERT OR IGNORE INTO policies VALUES (?,?)", (POLICY_VERSION, json.dumps(policy)))
        for item in corpus:
            exists = cx.execute("SELECT 1 FROM sources WHERE source_id=?", (item["source_id"],)).fetchone()
            if exists:
                continue
            cx.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?,?,?)", (item["source_id"], item["title"], item["classification"], item["authority_tier"], item["matter_id"], "1.0", json.dumps(item["allowed_actors"]), json.dumps(item["allowed_purposes"]), json.dumps(item["jurisdictions"]), item.get("url")))
            for i, text in enumerate(item["chunks"], 1):
                chunk_id = f'{item["source_id"]}-C{i:02}'
                cx.execute("INSERT INTO source_chunks VALUES (?,?,?,?)", (chunk_id, item["source_id"], text, hashlib.sha256(text.encode()).hexdigest()))
                cx.execute("INSERT INTO chunks_fts (chunk_id,text) VALUES (?,?)", (chunk_id, text))
