"""Release regressions: observability must not weaken the control boundary."""
import json
from dataclasses import replace
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import ROOT
from app.main import create_app
from app.providers.base import DraftResult, ModelUnavailable
from app.providers.diagnostics import safe_diagnostics
from app.providers.nebius import NebiusProvider
from app.services.presentation import evidence_view, receipt
from app.services.runs import RunService
from conftest import create_ready, headers, identity


def test_safe_receipt_is_explicit_allowlist_and_rechecks_identity(client, request_data):
    run_id = create_ready(client, request_data)
    identity(client, "alex_reviewer")
    client.post(f"/api/runs/{run_id}/review", headers=headers(client), json={
        "actor_id":"alex_reviewer","decision":"APPROVE","rationale":"PRIVATE REVIEW NOTE"})
    response = client.get(f"/api/runs/{run_id}/receipt")
    result = response.json()
    assert response.status_code == 200 and "attachment" in response.headers["content-disposition"]
    assert result["review"]["decision"] == "APPROVE"
    assert result["retrieval_attempts"] == 1 and result["provider_attempts"] == 0
    assert result["checks_passed"] == result["checks_total"] == 10
    assert result["provider_completed"] is False and result["audit_valid"] is True
    assert not {"question","rationale","evidence","scope","draft","audit"} & result.keys()
    for forbidden in ("PRIVATE REVIEW NOTE",request_data["question"],"SYSTEM:","ORCHID-RESTRICTED-772"):
        assert forbidden not in response.text
    identity(client,"maya_privacy_counsel")
    assert client.get(f"/api/runs/{run_id}/receipt").status_code == 403


def test_denial_receipt_measures_zero_and_never_retrieves(service, research_request, monkeypatch):
    from app.services import retrieval
    spy = Mock(side_effect=AssertionError("denial must stop before retrieval"))
    monkeypatch.setattr(retrieval,"retrieve",spy)
    provider = Mock(side_effect=AssertionError("denial must stop before inference"))
    service.providers["fixture"].generate_draft = provider
    run_id = service.create(research_request.model_copy(update={"matter_id":"restricted_m_and_a","purpose":"transaction_analysis"}))
    service.execute(run_id)
    result = receipt(service.get(run_id,research_request.actor_id))
    assert result["retrieval_attempts"] == result["provider_attempts"] == 0
    assert result["evidence_count"] is None
    assert not spy.called and not provider.called
    assert "RES-MA-001" not in json.dumps(result)


def test_legacy_run_receipt_does_not_invent_operation_counts(service, research_request, monkeypatch):
    original = service.db.append_event
    def legacy(cx, run_id, event_type, payload=None, actor_id=None):
        payload = dict(payload or {})
        payload.pop("instrumentation_version",None)
        payload.pop("transport_observed",None)
        return original(cx,run_id,event_type,payload,actor_id)
    monkeypatch.setattr(service.db,"append_event",legacy)
    run_id = service.create(research_request)
    service.execute(run_id)
    result = receipt(service.get(run_id,research_request.actor_id))
    assert result["retrieval_attempts"] is None and result["provider_attempts"] is None
    assert result["checks_passed"] == 10


@pytest.mark.parametrize("http_status,code",[(401,"PROVIDER_AUTH_ERROR"),(403,"PROVIDER_AUTH_ERROR"),
    (429,"PROVIDER_RATE_LIMITED"),(503,"PROVIDER_HTTP_ERROR")])
def test_provider_failure_diagnostics_and_live_status(db, settings, request_data, http_status, code):
    settings = replace(settings,api_key="private-test-key")
    provider = NebiusProvider(settings, transport=httpx.MockTransport(lambda _:httpx.Response(
        http_status,headers={"x-request-id":"request-123"},json={"secret":"PRIVATE UPSTREAM BODY"})))
    with TestClient(create_app(settings,database=db,live_provider=provider)) as client:
        run_id = client.post("/api/runs",headers=headers(client),json=request_data|{"mode":"live"}).json()["run_id"]
        run = client.get(f"/api/runs/{run_id}").json()
        assert run["status"] == "MODEL_UNAVAILABLE" and run["error_code"] == code
        assert run["provider"]["http_status"] == http_status
        result = client.get(f"/api/runs/{run_id}/receipt").json()
        assert result["provider_attempts"] == 1 and result["retrieval_attempts"] == 1
        assert result["provider"]["request_id"] == "request-123"
        assert not client.get("/api/status").json()["live_verified"]
        for path in (f"/api/runs/{run_id}",f"/api/runs/{run_id}/receipt",f"/runs/{run_id}/audit"):
            text = client.get(path).text
            assert "PRIVATE UPSTREAM BODY" not in text and settings.api_key not in text
        assert "Start separate fixture demo" in client.get(f"/runs/{run_id}").text


def test_repair_attempts_are_measured_at_transport_boundary(db, settings, research_request):
    calls = []
    def respond(request):
        calls.append(request)
        content = "invalid" if len(calls) == 1 else (ROOT/"seed/vendor-fixture.json").read_text()
        return httpx.Response(200,json={"id":"request-2","choices":[{"finish_reason":"stop","message":{"content":content}}],
            "usage":{"prompt_tokens":1234,"completion_tokens":870}})
    settings = replace(settings,api_key="mock-private-key")
    service = RunService(db,settings,live_provider=NebiusProvider(settings,transport=httpx.MockTransport(respond)))
    run_id = service.create(research_request.model_copy(update={"mode":"live"}))
    service.execute(run_id)
    run = service.get(run_id,research_request.actor_id)
    result = receipt(run)
    assert len(calls) == result["provider_attempts"] == 2
    assert result["provider_completed"] and run["status"] == "READY_FOR_REVIEW"
    assert result["provider"]["output_tokens"] == 870
    assert result["provider"]["input_tokens"] == 1234
    assert result["provider"]["finish_reason"] == "stop"
    types = [e["event_type"] for e in run["audit"]]
    assert types.index("POLICY_RESOLVED") < types.index("RETRIEVAL_STARTED") < types.index("TRANSPORT_ATTEMPTED")


def test_length_failure_retains_only_validated_diagnostics(db,settings,research_request,capsys):
    payload = {"id":"bad\nrequest-id","choices":[{"finish_reason":"length","message":{"content":"PRIVATE PARTIAL OUTPUT"}}],
               "usage":{"prompt_tokens":True,"completion_tokens":900}}
    settings = replace(settings,api_key="mock-private-key")
    service = RunService(db,settings,live_provider=NebiusProvider(settings,transport=httpx.MockTransport(lambda _:httpx.Response(200,json=payload))))
    run_id = service.create(research_request.model_copy(update={"mode":"live"})); service.execute(run_id)
    run = service.get(run_id,research_request.actor_id)
    assert run["error_code"] == "PROVIDER_INCOMPLETE_OUTPUT"
    assert run["provider"]["finish_reason"] == "length" and run["provider"]["output_tokens"] == 900
    assert "input_tokens" not in run["provider"] and "request_id" not in run["provider"]
    assert "PRIVATE PARTIAL OUTPUT" not in json.dumps(run)+capsys.readouterr().out


@pytest.mark.parametrize("values",[
    {"output_tokens":-1,"input_tokens":True,"attempt":3,"http_status":999,"latency_ms":float("inf")},
    {"finish_reason":[],"request_id":"x"*161,"output_tokens":"900"},
    {"finish_reason":"SECRET RESPONSE BODY","raw":"private","authorization":"Bearer secret"},
])
def test_diagnostics_reject_malformed_or_nonallowlisted_values(values):
    assert safe_diagnostics(values) == {}


def test_timeout_reports_actual_attempt_without_body(db,settings,research_request):
    def timeout(_):
        raise httpx.ReadTimeout("PRIVATE EXCEPTION MESSAGE")
    settings = replace(settings,api_key="mock-private-key")
    service = RunService(db,settings,live_provider=NebiusProvider(settings,transport=httpx.MockTransport(timeout)))
    run_id = service.create(research_request.model_copy(update={"mode":"live"})); service.execute(run_id)
    run = service.get(run_id,research_request.actor_id)
    assert run["error_code"] == "PROVIDER_TIMEOUT"
    assert receipt(run)["provider_attempts"] == 1
    assert "PRIVATE EXCEPTION MESSAGE" not in json.dumps(run)


def test_inline_evidence_uses_exact_claim_links_and_escapes_text(client,request_data):
    run_id = create_ready(client,request_data)
    run = client.get(f"/api/runs/{run_id}").json()
    view = evidence_view(run)
    material = [s for section in view["sections"] for s in section["statements"]]
    assert len(material) == 1+len(run["draft"]["conditions"])+len(run["draft"]["risks_and_caveats"])
    assert all(s["refs"] for s in material)
    page = client.get(f"/runs/{run_id}/brief").text
    for statement in material:
        assert f'id="{statement["anchor"]}"' in page
        for ref in statement["refs"]:
            assert f'href="#{ref["chunk_id"]}" data-evidence-link' in page
    assert "Claim-to-evidence links" not in page
    run["draft"]["summary"] = "A similar but unlinked statement"
    assert evidence_view(run)["sections"][0]["statements"][0]["refs"] == []


def test_history_filters_remain_scoped_to_requester(client,request_data):
    jordan = create_ready(client,request_data)
    identity(client,"maya_privacy_counsel")
    maya = create_ready(client,request_data|{"actor_id":"maya_privacy_counsel"})
    assert jordan not in client.get("/?filter=review").text
    assert maya in client.get("/?filter=review").text
    completed_ledger = client.get("/?filter=completed").text.split('id="research-ledger"',1)[1]
    assert maya not in completed_ledger
    identity(client,"alex_reviewer")
    text = client.get("/?filter=review").text
    assert jordan in text and maya in text


def test_receipt_export_refuses_corrupt_audit(client,request_data,db):
    run_id = create_ready(client,request_data)
    with db.transaction() as cx:
        cx.execute("DROP TRIGGER audit_no_update")
        cx.execute("UPDATE audit_events SET event_type='CORRUPTED' WHERE run_id=? AND sequence_number=1",(run_id,))
    assert client.get(f"/api/runs/{run_id}/receipt").status_code == 503


def test_approval_copy_never_approves_underlying_business_action(client,request_data):
    run_id = create_ready(client,request_data)
    identity(client,"alex_reviewer")
    client.post(f"/api/runs/{run_id}/review",headers=headers(client),json={"actor_id":"alex_reviewer","decision":"APPROVE"})
    page = client.get(f"/runs/{run_id}/review").text
    assert "Research draft approved" in page
    assert "does not authorize data sharing" in page


def test_denied_and_control_blocked_runs_have_no_fixture_bypass(client,request_data):
    denied = client.post("/api/runs",headers=headers(client),json=request_data|{"matter_id":"restricted_m_and_a","purpose":"transaction_analysis"}).json()["run_id"]
    assert "Start separate fixture demo" not in client.get(f"/runs/{denied}").text
    raw = json.loads((ROOT/"seed/vendor-fixture.json").read_text())
    raw["citations"][0]["chunk_ids"] = ["unknown"]
    client.app.state.service.providers["fixture"] = Mock(generate_draft=Mock(return_value=DraftResult(json.dumps(raw),"fixture","mock",None,0)))
    blocked = client.post("/api/runs",headers=headers(client),json=request_data).json()["run_id"]
    page = client.get(f"/runs/{blocked}").text
    assert "Start separate fixture demo" not in page and "Draft withheld by controls" in page


def test_open_existing_database_preserves_decision_and_audit(tmp_path,settings,research_request):
    from app.persistence.db import Database
    from app.seed import seed
    from app.services.review import decide
    path = str(tmp_path/"existing.sqlite3")
    db = Database(path); seed(db)
    service = RunService(db,settings)
    run_id = service.create(research_request); service.execute(run_id)
    decide(db,run_id,"alex_reviewer","APPROVE","Original recorded note")
    before = service.get(run_id,research_request.actor_id)
    db.close()
    reopened = Database(path); seed(reopened)
    after = RunService(reopened,settings).get(run_id,research_request.actor_id)
    assert before == after
    reopened.close()
