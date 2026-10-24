import json
import secrets
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.sessions import SessionMiddleware

from app.config import ROOT, Settings
from app.domain import DISCLOSURE, QUESTION, ResearchRequest, ControlError
from app.persistence.db import Database
from app.seed import USERS, seed
from app.services.runs import RunService
from app.services.review import decide, ReviewConflict


def create_app(settings=None, *, database=None, live_provider=None, fixture_provider=None):
    settings = settings or Settings()
    db = database or Database(settings.database)
    seed(db)
    service = RunService(db,settings,live_provider,fixture_provider)

    @asynccontextmanager
    async def lifespan(app):
        service.recover_interrupted()
        yield
        if database is None:
            db.close()

    app = FastAPI(title="MatterGate",lifespan=lifespan,docs_url=None,redoc_url=None)
    app.state.db, app.state.service, app.state.settings = db, service, settings
    app.add_middleware(SessionMiddleware,secret_key=settings.session_secret,same_site="strict",max_age=28800)
    app.mount("/static",StaticFiles(directory=ROOT / "static"),name="static")
    templates = Jinja2Templates(directory=ROOT / "templates")
    limits = defaultdict(deque)

    def session(request):
        if "actor" not in request.session:
            request.session.update(actor="jordan_sales_ops",csrf=secrets.token_urlsafe(32),sid=secrets.token_urlsafe(24))
        return request.session

    def mutation(request):
        state = session(request)
        token = request.headers.get("x-csrf-token", "")
        origin = request.headers.get("origin")
        if not secrets.compare_digest(token,state["csrf"]) or (origin and origin.rstrip("/") != str(request.base_url).rstrip("/")):
            raise HTTPException(403,"CSRF_CHECK_FAILED")
        return state["actor"]

    def view(request,run_id):
        try:
            return service.get(run_id,session(request)["actor"])
        except LookupError:
            raise HTTPException(404,"RUN_NOT_FOUND") from None
        except PermissionError:
            raise HTTPException(403,"RUN_NOT_AUTHORIZED") from None
        except ControlError:
            raise HTTPException(503,"CONTROL_INTEGRITY_FAILED") from None

    def status():
        return {"app_mode":"demo","provider_mode":"live" if settings.live_ready else "fixture",
            "provider":"nebius" if settings.live_ready else "fixture","model_id":settings.model,
            "database_ready":db.one("SELECT count(*) AS n FROM sources")["n"] >= 6,
            "seed_data_version":"1.0","live_configured":settings.live_ready,
            "live_verified":bool(db.one("SELECT 1 FROM research_runs WHERE mode='live' AND provider_json IS NOT NULL AND json_extract(provider_json,'$.provider')='nebius' LIMIT 1")),
            "upstream_commit":"21baa4ccdc468bd6a30681344eb8ec3df752790a"}

    def render(request,name,**context):
        actor = session(request)["actor"]
        runs = db.rows("SELECT run_id,actor_id,matter_id,status,mode,created_at FROM research_runs "+("" if actor == "alex_reviewer" else "WHERE actor_id=? ")+"ORDER BY created_at DESC LIMIT 12",() if actor == "alex_reviewer" else (actor,))
        return templates.TemplateResponse(request=request,name=name,context={
            "actor_id":actor,"user":USERS[actor],"users":USERS,"csrf":request.session["csrf"],
            "system":status(),"disclosure":DISCLOSURE,"runs":runs,"question":QUESTION,**context})

    @app.middleware("http")
    async def security_headers(request,call_next):
        response = await call_next(request)
        response.headers.update({"X-Content-Type-Options":"nosniff","Referrer-Policy":"same-origin",
            "Cache-Control":"no-store","Content-Security-Policy":"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"})
        return response

    @app.get("/api/session")
    def get_session(request: Request):
        state = session(request)
        return {"actor_id":state["actor"],"csrf_token":state["csrf"],"users":USERS}

    class IdentityBody(BaseModel):
        model_config = ConfigDict(extra="forbid")
        actor_id: Literal["jordan_sales_ops","maya_privacy_counsel","alex_reviewer"]

    @app.post("/api/session")
    def switch_identity(body: IdentityBody,request: Request):
        mutation(request)
        request.session.update(actor=body.actor_id,csrf=secrets.token_urlsafe(32))
        return {"actor_id":body.actor_id,"csrf_token":request.session["csrf"]}

    @app.post("/api/runs",status_code=202)
    def create_run(body: ResearchRequest,request: Request,background: BackgroundTasks):
        actor = mutation(request)
        if actor != body.actor_id:
            raise HTTPException(403,"REQUESTER_SESSION_MISMATCH")
        queue = limits[request.session["sid"]]
        while queue and time.monotonic()-queue[0] > 60:
            queue.popleft()
        if len(queue) >= 6:
            raise HTTPException(429,"RUN_LIMIT_REACHED")
        if body.mode == "live" and not settings.live_ready:
            raise HTTPException(422,"LIVE_PROVIDER_NOT_CONFIGURED")
        queue.append(time.monotonic())
        try:
            run_id = service.create(body)
        except Exception:
            raise HTTPException(503,"RUN_PERSISTENCE_FAILED") from None
        background.add_task(service.execute,run_id)
        return {"run_id":run_id,"status":"RECEIVED","status_url":f"/api/runs/{run_id}","brief_url":f"/runs/{run_id}/brief","audit_url":f"/runs/{run_id}/audit"}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str,request: Request):
        return view(request,run_id)

    class ReviewBody(BaseModel):
        model_config = ConfigDict(extra="forbid")
        actor_id: str
        decision: Literal["APPROVE","REJECT","REQUEST_REVISION"]
        rationale: str = Field(default="",max_length=1000)

    @app.post("/api/runs/{run_id}/review")
    def review_run(run_id: str,body: ReviewBody,request: Request):
        actor = mutation(request)
        if actor != body.actor_id:
            raise HTTPException(403,"REVIEWER_SESSION_MISMATCH")
        try:
            result = decide(db,run_id,actor,body.decision,body.rationale)
            return {"run_id":run_id,"status":result}
        except PermissionError:
            raise HTTPException(403,"REVIEWER_REQUIRED") from None
        except ReviewConflict:
            raise HTTPException(409,"REVIEW_NOT_AVAILABLE") from None
        except LookupError:
            raise HTTPException(404,"RUN_NOT_FOUND") from None
        except ControlError:
            raise HTTPException(503,"CONTROL_INTEGRITY_FAILED") from None
        except ValueError:
            raise HTTPException(422,"RATIONALE_REQUIRED") from None
        except Exception:
            raise HTTPException(503,"REVIEW_PERSISTENCE_FAILED") from None

    @app.get("/api/status")
    def api_status():
        return status()

    @app.get("/",response_class=HTMLResponse)
    def home(request: Request):
        return render(request,"home.html",page="home")

    @app.get("/runs/new",response_class=HTMLResponse)
    def new_run(request: Request):
        return render(request,"new.html",page="new")

    @app.get("/status",response_class=HTMLResponse)
    def system_status(request: Request):
        return render(request,"status.html",page="status")

    @app.get("/runs/{run_id}",response_class=HTMLResponse)
    @app.get("/runs/{run_id}/{tab}",response_class=HTMLResponse)
    def run_workspace(run_id: str,request: Request,tab: str="progress"):
        if tab not in {"progress","brief","review","audit"}:
            raise HTTPException(404)
        run = view(request,run_id)
        return render(request,"run.html",page="run",run=run,tab=tab)

    return app


app = create_app()
