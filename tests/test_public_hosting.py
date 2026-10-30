"""Public hosting must isolate visitors and bound actual paid transports."""
from dataclasses import replace
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import ROOT
from app.main import create_app
from app.providers.nebius import NebiusProvider
from app.services.runs import RunService
from app.services.admission import AdmissionError, RequestLimits
from conftest import headers, identity, create_ready


def public_settings(settings, **changes):
    return replace(settings,public_demo=True,public_origin="https://demo.example.com",
                   session_secret="s"*48,**changes)


def test_public_workspaces_cover_all_routes_and_reviewer(db,settings,request_data):
    app = create_app(public_settings(settings),database=db)
    with TestClient(app,base_url="https://demo.example.com") as first, TestClient(app,base_url="https://demo.example.com") as other:
        run_id = create_ready(first,request_data)
        assert all(cookie.secure for cookie in first.cookies.jar)
        assert run_id not in other.get("/").text
        identity(other,"alex_reviewer")
        for path in (f"/api/runs/{run_id}",f"/api/runs/{run_id}/receipt",f"/runs/{run_id}/brief",f"/runs/{run_id}/audit"):
            assert other.get(path).status_code == 404
        assert other.post(f"/api/runs/{run_id}/review",headers=headers(other),json={"actor_id":"alex_reviewer","decision":"APPROVE"}).status_code == 404
        identity(first,"alex_reviewer")
        assert first.post(f"/api/runs/{run_id}/review",headers=headers(first),json={"actor_id":"alex_reviewer","decision":"APPROVE"}).status_code == 200
        assert first.get(f"/api/runs/{run_id}/receipt").json()["status"] == "APPROVED"
        assert app.state.db.verify_chain(run_id)
        assert other.get("/healthz").json() == {"status":"ok"}
        assert other.get("/",headers={"host":"evil.example"}).status_code == 400


def test_public_origin_check(db,settings,request_data):
    with TestClient(create_app(public_settings(settings),database=db),base_url="https://demo.example.com") as client:
        assert client.post("/api/runs",json=request_data,headers=headers(client)|{"Origin":"https://evil.example"}).status_code == 403
        assert client.post("/api/runs",json=request_data,headers=headers(client)|{"Origin":"https://demo.example.com"}).status_code == 202


@pytest.mark.parametrize("daily,monthly",[(1,100),(100,1)])
def test_quota_counts_repairs_and_persists_across_service_restart(db,settings,research_request,daily,monthly):
    calls = []
    def respond(request):
        calls.append(request)
        return httpx.Response(200,json={"id":"mock","choices":[{"finish_reason":"stop","message":{"content":"invalid json"}}]})
    cfg = public_settings(settings,api_key="test-key",live_daily_limit=daily,live_monthly_limit=monthly)
    provider = NebiusProvider(cfg,transport=httpx.MockTransport(respond))
    for workspace in ("first", "second"):
        service = RunService(db,cfg,live_provider=provider)
        run_id = service.create(research_request.model_copy(update={"mode":"live"}),workspace_id=workspace)
        service.execute(run_id)
        run = service.get(run_id,research_request.actor_id)
        assert run["error_code"] == "PUBLIC_LIVE_QUOTA_REACHED"
        assert db.verify_chain(run_id)
    assert len(calls) == 1
    assert all(r["attempts"] == 1 for r in db.rows("SELECT * FROM public_usage"))


def test_quota_reservation_is_atomic_between_concurrent_runs(db,settings,research_request):
    calls = []
    def respond(request):
        calls.append(request)
        return httpx.Response(200,json={"id":"mock","choices":[{"finish_reason":"stop","message":{"content":(ROOT/"seed/vendor-fixture.json").read_text()}}]})
    cfg = public_settings(settings,api_key="test-key",live_daily_limit=1)
    service = RunService(db,cfg,live_provider=NebiusProvider(cfg,transport=httpx.MockTransport(respond)))
    ids = [service.create(research_request.model_copy(update={"mode":"live"}),workspace_id=str(i)) for i in range(2)]
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(service.execute,ids))
    assert len(calls) == 1
    assert sorted(service.get(i,research_request.actor_id)["status"] for i in ids) == ["MODEL_UNAVAILABLE","READY_FOR_REVIEW"]


def test_public_admission_and_ip_limit(db,settings,research_request):
    service = RunService(db,public_settings(settings))
    with pytest.raises(AdmissionError,match="WORKSPACE_REQUIRED"):
        service.create(research_request)
    for i in range(4):
        service.create(research_request,workspace_id=str(i))
    with pytest.raises(AdmissionError,match="SERVER_BUSY"):
        service.create(research_request,workspace_id="overflow")
    limiter = RequestLimits()
    for i in range(20):
        limiter.check(str(i),"same-address")
    with pytest.raises(AdmissionError,match="RUN_LIMIT_REACHED"):
        limiter.check("new-browser","same-address")


def test_hosted_configuration_fails_closed(settings):
    with pytest.raises(ValueError):
        replace(settings,public_demo=True,public_origin="http://example.com")
    assert not replace(settings,live_enabled=False,api_key="present").live_ready
