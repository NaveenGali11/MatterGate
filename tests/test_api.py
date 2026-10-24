import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.domain import ControlError
from app.services.review import decide, ReviewConflict
from conftest import headers, identity, create_ready


@pytest.mark.parametrize("path",["/","/runs/new","/status","/api/status","/static/app.js","/static/app.css"])
def test_pages_and_assets_render(client,path):
    response=client.get(path)
    assert response.status_code==200
    assert response.headers["x-content-type-options"]=="nosniff"


def test_full_run_review_and_ledger(client,request_data):
    run_id=create_ready(client,request_data)
    for suffix in ("","/brief","/review","/audit"):
        assert client.get("/runs/"+run_id+suffix).status_code==200
    result=client.get("/api/runs/"+run_id).json()
    assert result["audit_valid"] and all(c["passed"] for c in result["checks"])
    assert not any(e["event_type"]=="MODEL_REQUESTED" for e in result["audit"])
    identity(client,"alex_reviewer")
    response=client.post(f"/api/runs/{run_id}/review",json={"actor_id":"alex_reviewer","decision":"APPROVE","rationale":"Synthetic assessment reviewed."},headers=headers(client))
    assert response.status_code==200
    result=client.get("/api/runs/"+run_id).json()
    assert result["status"]=="APPROVED" and result["review"]["actor_id"]=="alex_reviewer"
    assert result["audit"][-1]["event_type"]=="REVIEW_SUBMITTED"
    assert client.post(f"/api/runs/{run_id}/review",json={"actor_id":"alex_reviewer","decision":"APPROVE"},headers=headers(client)).status_code==409


def test_forged_reviewer_and_requester_are_rejected(client,request_data):
    run_id=create_ready(client,request_data)
    assert client.post(f"/api/runs/{run_id}/review",json={"actor_id":"alex_reviewer","decision":"APPROVE"},headers=headers(client)).status_code==403
    assert client.post(f"/api/runs/{run_id}/review",json={"actor_id":"jordan_sales_ops","decision":"APPROVE"},headers=headers(client)).status_code==403
    assert client.post("/api/runs",json=request_data|{"actor_id":"maya_privacy_counsel"},headers=headers(client)).status_code==403


@pytest.mark.parametrize("decision",["REJECT","REQUEST_REVISION"])
def test_review_rationale_required_and_decision_recorded(client,request_data,decision):
    run_id=create_ready(client,request_data)
    identity(client,"alex_reviewer")
    url=f"/api/runs/{run_id}/review"
    body={"actor_id":"alex_reviewer","decision":decision,"rationale":"   "}
    assert client.post(url,json=body,headers=headers(client)).status_code==422
    body["rationale"]="Please resolve the DPA and deletion questions."
    assert client.post(url,json=body,headers=headers(client)).status_code==200
    assert client.get("/api/runs/"+run_id).json()["status"]=={"REJECT":"REJECTED","REQUEST_REVISION":"REVISION_REQUESTED"}[decision]


def test_csrf_and_origin_controls(client,request_data):
    assert client.post("/api/runs",json=request_data).status_code==403
    assert client.post("/api/runs",json=request_data,headers=headers(client)|{"Origin":"https://attacker.invalid"}).status_code==403


def test_denial_is_nonrevealing(client,request_data):
    response=client.post("/api/runs",json=request_data|{"matter_id":"restricted_m_and_a","purpose":"transaction_analysis"},headers=headers(client))
    run_id=response.json()["run_id"]
    body=client.get("/api/runs/"+run_id)
    assert body.json()["status"]=="DENIED"
    for path in ("/api/runs/","/runs/"):
        text=client.get(path+run_id).text
        assert "ORCHID-RESTRICTED-772" not in text and "RES-MA-001" not in text
        assert "Synthetic transaction work product" not in text
    identity(client,"alex_reviewer")
    assert client.post(f"/api/runs/{run_id}/review",json={"actor_id":"alex_reviewer","decision":"REJECT","rationale":"Test"},headers=headers(client)).status_code==409


def test_run_reads_enforce_session_owner(client,request_data):
    run_id=create_ready(client,request_data)
    identity(client,"maya_privacy_counsel")
    assert client.get("/api/runs/"+run_id).status_code==403
    assert client.get("/runs/"+run_id+"/brief").status_code==403


def test_live_unconfigured_cannot_be_silently_fixture(client,request_data):
    response=client.post("/api/runs",json=request_data|{"mode":"live"},headers=headers(client))
    assert response.status_code==422
    assert client.get("/api/status").json()["provider"]=="fixture"


def test_validation_and_rate_limit(client,request_data):
    for change in ({"question":"too short"},{"question":"<script>alert('not plain')</script>"},{"question":"x"*1001},{"extra":"bad"}):
        assert client.post("/api/runs",json=request_data|change,headers=headers(client)).status_code==422
    for _ in range(6):
        assert client.post("/api/runs",json=request_data,headers=headers(client)).status_code==202
    assert client.post("/api/runs",json=request_data,headers=headers(client)).status_code==429


def test_concurrent_review_has_one_winner(service,research_request):
    run_id=service.create(research_request); service.execute(run_id)
    def submit(_):
        try:
            return decide(service.db,run_id,"alex_reviewer","APPROVE","")
        except ReviewConflict:
            return "CONFLICT"
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(submit,range(2)))==["APPROVED","CONFLICT"]


def test_audit_is_immutable_and_tampering_detected(client,request_data,db):
    run_id=create_ready(client,request_data)
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        with db.transaction() as cx:
            cx.execute("UPDATE audit_events SET event_type='TAMPERED' WHERE run_id=?",(run_id,))
    with db.transaction() as cx:
        cx.execute("DROP TRIGGER audit_no_update")
        cx.execute("UPDATE audit_events SET event_type='TAMPERED' WHERE run_id=? AND sequence_number=1",(run_id,))
    assert not db.verify_chain(run_id)
    assert client.get("/api/runs/"+run_id).status_code==503


def test_failed_audit_append_rolls_back_review(service,research_request,monkeypatch):
    run_id=service.create(research_request); service.execute(run_id)
    def fail(*args,**kwargs): raise RuntimeError("simulated disk failure")
    monkeypatch.setattr(service.db,"append_event",fail)
    with pytest.raises(RuntimeError): decide(service.db,run_id,"alex_reviewer","APPROVE","")
    assert service.db.one("SELECT status FROM research_runs WHERE run_id=?",(run_id,))["status"]=="READY_FOR_REVIEW"
    assert service.db.one("SELECT * FROM review_decisions WHERE run_id=?",(run_id,)) is None


def test_invalid_state_transition_is_rejected(service,research_request):
    run_id=service.create(research_request)
    with pytest.raises(ControlError): service.db.transition(run_id,"APPROVED","REVIEW_SUBMITTED")


def test_restart_marks_interrupted_runs_blocked(service,research_request):
    run_id=service.create(research_request)
    service.recover_interrupted()
    result=service.get(run_id,research_request.actor_id)
    assert result["status"]=="BLOCKED" and result["error_code"]=="PROCESS_INTERRUPTED"


def test_failed_audit_append_never_commits_ready_state(service,research_request,monkeypatch):
    original=service.db.append_event
    def fail_ready(cx,run_id,event_type,*args,**kwargs):
        if event_type=="READY_FOR_REVIEW": raise RuntimeError("simulated disk failure")
        return original(cx,run_id,event_type,*args,**kwargs)
    monkeypatch.setattr(service.db,"append_event",fail_ready)
    run_id=service.create(research_request);service.execute(run_id)
    result=service.get(run_id,research_request.actor_id)
    assert result["status"]=="BLOCKED" and result["draft"] is None
    assert not service.db.rows("SELECT * FROM evaluation_results WHERE run_id=?",(run_id,))


def test_tampered_source_text_is_not_served_as_original(client,request_data,db):
    run_id=create_ready(client,request_data)
    with db.transaction() as cx:
        cx.execute("UPDATE source_chunks SET text='Corrupted synthetic source' WHERE source_id='INT-DPA-001'")
    assert client.get("/api/runs/"+run_id).status_code==503
