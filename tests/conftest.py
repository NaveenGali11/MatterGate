import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.domain import QUESTION, ResearchRequest
from app.main import create_app
from app.persistence.db import Database
from app.seed import seed
from app.services.runs import RunService


@pytest.fixture
def db():
    instance = Database(":memory:")
    seed(instance)
    yield instance
    instance.close()


@pytest.fixture
def settings():
    return Settings(database=":memory:",session_secret="test-session-secret-not-for-deployment",api_key="",
        base_url="https://api.tokenfactory.nebius.com/v1",model="nvidia/Nemotron-3_5-Lightning")


@pytest.fixture
def request_data():
    return dict(actor_id="jordan_sales_ops",matter_id="vendor_onboarding",purpose="vendor_risk_assessment",jurisdiction="EU",question=QUESTION,mode="fixture")


@pytest.fixture
def research_request(request_data):
    return ResearchRequest(**request_data)


@pytest.fixture
def service(db,settings):
    return RunService(db,settings)


@pytest.fixture
def client(db,settings):
    with TestClient(create_app(settings,database=db)) as instance:
        yield instance


def headers(client):
    return {"X-CSRF-Token":client.get("/api/session").json()["csrf_token"]}


def identity(client,actor):
    response = client.post("/api/session",json={"actor_id":actor},headers=headers(client))
    assert response.status_code == 200


def create_ready(client,payload):
    response = client.post("/api/runs",json=payload,headers=headers(client))
    assert response.status_code == 202,response.text
    run_id = response.json()["run_id"]
    assert client.get("/api/runs/"+run_id).json()["status"] == "READY_FOR_REVIEW"
    return run_id
