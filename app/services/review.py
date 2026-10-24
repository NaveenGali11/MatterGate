"""Eligibility/conflict portions adapted from PriviLAB run_review.py, Apache-2.0.
Copyright 2026 Data Strategy Lab LLC. Modified: server session identity, ready-only
actions, required rationale, transactional decision and MatterGate audit chain.
Upstream: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
from uuid import uuid4

from app.domain import ControlError, now

DECISIONS = {"APPROVE":"APPROVED", "REJECT":"REJECTED", "REQUEST_REVISION":"REVISION_REQUESTED"}


class ReviewConflict(ControlError):
    pass


def decide(db, run_id, actor_id, decision, rationale):
    if actor_id != "alex_reviewer":
        raise PermissionError("REVIEWER_REQUIRED")
    if decision not in DECISIONS or (decision != "APPROVE" and not rationale.strip()):
        raise ValueError("RATIONALE_REQUIRED")
    with db.transaction() as cx:
        row = cx.execute("SELECT status FROM research_runs WHERE run_id=?",(run_id,)).fetchone()
        if row is None:
            raise LookupError("RUN_NOT_FOUND")
        if not db.verify_chain(run_id):
            raise ControlError("AUDIT_INTEGRITY_FAILED")
        checks = cx.execute("SELECT passed FROM evaluation_results WHERE run_id=?",(run_id,)).fetchall()
        if row[0] != "READY_FOR_REVIEW" or len(checks) < 10 or not all(check[0] for check in checks):
            raise ReviewConflict("REVIEW_NOT_AVAILABLE")
        if cx.execute("SELECT 1 FROM review_decisions WHERE run_id=?",(run_id,)).fetchone():
            raise ReviewConflict("REVIEW_ALREADY_RECORDED")
        cx.execute("INSERT INTO review_decisions VALUES (?,?,?,?,?,?)",(str(uuid4()),run_id,actor_id,decision,rationale.strip(),now()))
        cx.execute("UPDATE research_runs SET status=? WHERE run_id=?",(DECISIONS[decision],run_id))
        db.append_event(cx,run_id,"REVIEW_SUBMITTED",{"decision":decision,"status":DECISIONS[decision]},actor_id)
    return DECISIONS[decision]
