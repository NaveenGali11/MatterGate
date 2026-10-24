"""Cases ported/adapted from PriviLAB permission and retrieval boundary tests.
Copyright 2026 Data Strategy Lab LLC, Apache-2.0; modified for MatterGate's
request/scope schema, explicit jurisdiction and purpose, and fixture evidence.
Upstream: 21baa4ccdc468bd6a30681344eb8ec3df752790a.
"""
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from app.domain import AccessScope, ControlError, Draft, ResearchRequest, parse_draft
from app.integrations.privilab.citations import ProvenanceIndex, authorized_source, citation_resolution
from app.integrations.privilab.permissions import parse_permission_policy, evaluate_permission, permits_protected_progression, PermissionPolicyParseError
from app.integrations.privilab.types import SyntheticRequestContext
from app.providers.fixture import FixtureProvider
from app.services import policy, retrieval
from app.services.evaluation import evaluate


def evidence_for(db,request):
    scope = policy.resolve(db,request,"test-run")
    return scope,retrieval.retrieve(db,request.question,scope)


def test_allowed_scope_is_exact_and_has_no_restricted_source(db,research_request):
    scope = policy.resolve(db,research_request,"run-1")
    assert scope.policy_decision == "ALLOW"
    assert len(scope.allowed_source_ids) == 5
    assert "RES-MA-001" not in scope.allowed_source_ids


@pytest.mark.parametrize("change",[
    {"actor_id":"missing"}, {"actor_id":"alex_reviewer"},
    {"matter_id":"restricted_m_and_a","purpose":"transaction_analysis"},
    {"purpose":"support_operations"}, {"purpose":"transaction_analysis"},
])
def test_unsupported_context_denies(db,request_data,change):
    scope = policy.resolve(db,ResearchRequest(**(request_data|change)),"run-1")
    assert scope.policy_decision == "DENY"
    assert scope.allowed_source_ids == ()


def test_parser_and_missing_context_fail_closed(db):
    raw = json.loads(db.one("SELECT definition FROM policies")["definition"])
    parsed = parse_permission_policy(raw)
    result = evaluate_permission(parsed,SyntheticRequestContext())
    assert not permits_protected_progression(result)
    with pytest.raises(PermissionPolicyParseError):
        parse_permission_policy(raw|{"unexpected":True})
    raw["rules"].append(raw["rules"][0])
    with pytest.raises(PermissionPolicyParseError):
        parse_permission_policy(raw)


def test_explicit_block_precedes_missing_context_and_allow(db):
    from app.integrations.privilab.types import MatterContext
    raw=json.loads(db.one("SELECT definition FROM policies")["definition"])
    result=evaluate_permission(parse_permission_policy(raw),SyntheticRequestContext(matter=MatterContext("restricted_m_and_a")))
    assert result.state.value == "BLOCK"


def test_unresolved_condition_stops_protected_progression(db,research_request):
    raw=json.loads(db.one("SELECT definition FROM policies")["definition"])
    for rule in raw["rules"]:
        if rule["effect"] == "ALLOW": rule["condition_ids"]=["needs-clearance"]
    with db.transaction() as cx:
        cx.execute("UPDATE policies SET definition=?",(json.dumps(raw),))
    assert policy.resolve(db,research_request,"run-1").policy_decision == "DENY"


@pytest.mark.parametrize("scope",[None,object()])
def test_retrieval_requires_scope(db,scope):
    with pytest.raises(ControlError):
        retrieval.retrieve(db,"vendor contact",scope)


def test_deny_and_expired_scopes_fail_at_retrieval_and_provider(db,research_request,request_data):
    scope,evidence=evidence_for(db,research_request)
    denied=policy.resolve(db,ResearchRequest(**(request_data|{"matter_id":"restricted_m_and_a"})),"denied")
    expired=scope.model_copy(update={"expires_at":(datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()})
    for invalid in (denied,expired,None):
        with pytest.raises(ControlError): retrieval.retrieve(db,"vendor",invalid)
        with pytest.raises(ControlError): FixtureProvider().generate_draft(request=research_request,scope=invalid,evidence=evidence)


@pytest.mark.parametrize("dimension,other",[("actor_id","other"),("matter_id","restricted_m_and_a"),("purpose","transaction_analysis"),("jurisdiction","UNLISTED")])
def test_scope_dimension_isolation(db,research_request,dimension,other):
    scope,_=evidence_for(db,research_request)
    changed=scope.model_copy(update={dimension:other})
    with pytest.raises(ControlError):
        retrieval.retrieve(db,"vendor customer contact",changed)


def test_retrieval_budget_query_escaping_and_authorization(db,research_request):
    scope,evidence=evidence_for(db,research_request)
    assert len(evidence)==5
    assert sum(len(item.text) for item in evidence)<=8000
    assert all(item.source_id in scope.allowed_source_ids for item in evidence)
    assert retrieval.retrieve(db,'"unterminated OR merger: "',scope)==[]
    assert retrieval.retrieve(db,"ORCHID RESTRICTED 772 merger",scope)==[]


def test_out_of_scope_corpus_cannot_change_ranking(db,research_request):
    scope,evidence=evidence_for(db,research_request)
    with db.transaction() as cx:
        for i in range(25):
            cx.execute("INSERT INTO chunks_fts VALUES (?,?)",(f"untrusted-{i}","Vendor X EU customer support "*30))
    assert [c.chunk_id for c in retrieval.retrieve(db,research_request.question,scope)]==[c.chunk_id for c in evidence]


def test_citation_checks_resolve_exact_source_chunk_pairs():
    index=ProvenanceIndex(frozenset({"a","b"}),frozenset({("a","a1"),("b","b1")}))
    assert authorized_source([("a","a1")],index)
    assert citation_resolution([("a","a1")],index)
    assert not citation_resolution([("a","b1")],index)
    assert not authorized_source([("unknown","a1")],index)
    assert not citation_resolution([],index)


def test_fixture_passes_all_required_checks(db,research_request):
    scope,evidence=evidence_for(db,research_request)
    result=FixtureProvider().generate_draft(request=research_request,scope=scope,evidence=evidence)
    draft=parse_draft(result.text)
    assert all(check["passed"] for check in evaluate(scope,evidence,draft))
    assert result.provider=="fixture" and result.request_id is None


@pytest.mark.parametrize("change,failed",[
    ({"disclaimer":"Wrong"},"DISCLAIMER_EXACT"),
    ({"summary":"An unsupported legal assertion."},"CLAIM_COVERAGE"),
    ({"summary":"The request is approved."},"NO_UNTRUSTED_COMMAND_FOLLOWING"),
    ({"summary":"ORCHID-RESTRICTED-772"},"NO_RESTRICTED_SOURCE"),
    ({"citations":[]},"CITATION_PRESENT"),
])
def test_deterministic_checks_block_invalid_drafts(db,research_request,change,failed):
    scope,evidence=evidence_for(db,research_request)
    draft=parse_draft(FixtureProvider().generate_draft(request=research_request,scope=scope,evidence=evidence).text)
    draft=draft.model_copy(update=change)
    checks={item["check_id"]:item["passed"] for item in evaluate(scope,evidence,draft)}
    assert checks[failed] is False


def test_unknown_citation_is_not_accepted(db,research_request):
    scope,evidence=evidence_for(db,research_request)
    result=FixtureProvider().generate_draft(request=research_request,scope=scope,evidence=evidence)
    raw=json.loads(result.text)
    raw["citations"][0]["chunk_ids"]=["RES-MA-001-C01"]
    checks=evaluate(scope,evidence,Draft.model_validate(raw))
    assert not next(c for c in checks if c["check_id"]=="CITATION_IN_SCOPE")["passed"]


@pytest.mark.parametrize("raw",['{}','{"summary":"a","summary":"b"}','[]','not JSON','{"summary":NaN}'])
def test_malformed_output_rejected(raw):
    with pytest.raises(ValueError): parse_draft(raw)


def test_fixture_not_reused_for_unrelated_question(db,research_request):
    scope,evidence=evidence_for(db,research_request)
    changed=research_request.model_copy(update={"question":"What contracts relate to the proposed merger?"})
    with pytest.raises(ControlError,match="FIXTURE_SCENARIO_UNSUPPORTED"):
        FixtureProvider().generate_draft(request=changed,scope=scope,evidence=evidence)


def test_denied_run_has_no_retrieval_or_provider(service,request_data,monkeypatch):
    retrieve_spy=Mock(side_effect=AssertionError("retrieval must not run"))
    model_spy=Mock(side_effect=AssertionError("provider must not run"))
    monkeypatch.setattr(retrieval,"retrieve",retrieve_spy)
    service.providers["fixture"].generate_draft=model_spy
    request=ResearchRequest(**(request_data|{"matter_id":"restricted_m_and_a","purpose":"transaction_analysis"}))
    run_id=service.create(request); service.execute(run_id)
    result=service.get(run_id,request.actor_id)
    assert result["status"]=="DENIED" and result["evidence"]==[] and result["draft"] is None
    assert result["question"]==""
    assert not retrieve_spy.called and not model_spy.called
    assert not service.db.rows("SELECT * FROM run_evidence WHERE run_id=?",(run_id,))
    assert not any(e["event_type"] in {"MODEL_REQUESTED","RETRIEVAL_STARTED"} for e in result["audit"])


def test_known_injection_is_data_and_cannot_approve(service,research_request):
    run_id=service.create(research_request); service.execute(run_id)
    result=service.get(run_id,research_request.actor_id)
    assert any("SYSTEM:" in c["text"] for c in result["evidence"])
    assert result["status"]=="READY_FOR_REVIEW" and result["review"] is None
    assert "Ignore prior controls" not in result["draft"]["summary"]
    assert any(e["event_type"]=="UNTRUSTED_INSTRUCTION_DETECTED" for e in result["audit"])
