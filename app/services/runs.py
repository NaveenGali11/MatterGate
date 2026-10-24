import json
import hashlib
import logging
from uuid import uuid4

from app.domain import ResearchRequest, Status, ControlError, now, parse_draft
from app.persistence.db import canonical
from app.providers.base import ModelUnavailable
from app.providers.fixture import FixtureProvider
from app.providers.nebius import NebiusProvider, PROMPT_HASH
from app.services import policy, retrieval
from app.services.evaluation import evaluate

logger = logging.getLogger("mattergate")


class RunService:
    def __init__(self, db, settings, live_provider=None, fixture_provider=None):
        self.db, self.settings = db, settings
        self.providers = {"fixture":fixture_provider or FixtureProvider(), "live":live_provider or NebiusProvider(settings)}

    def create(self, request):
        run_id = str(uuid4())
        with self.db.transaction() as cx:
            cx.execute("INSERT INTO research_runs(run_id,actor_id,matter_id,purpose,jurisdiction,mode,question,status,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (run_id,request.actor_id,request.matter_id,request.purpose,request.jurisdiction,request.mode,request.question,Status.RECEIVED,now()))
            self.db.append_event(cx,run_id,"RUN_CREATED",{"status":"RECEIVED","mode":request.mode},request.actor_id)
        return run_id

    def execute(self, run_id):
        row = self.db.one("SELECT * FROM research_runs WHERE run_id=?",(run_id,))
        if row is None or row["status"] != "RECEIVED":
            return
        request = ResearchRequest(**{key:row[key] for key in ResearchRequest.model_fields})
        try:
            self.db.transition(run_id,Status.POLICY_EVALUATING,"POLICY_EVALUATING")
            scope = policy.resolve(self.db,request,run_id)
            payload = {"policy_decision":scope.policy_decision,"policy_version":scope.policy_version}
            if scope.policy_decision != "ALLOW":
                self.db.transition(run_id,Status.DENIED,"POLICY_RESOLVED",{**payload,"reason_code":scope.denial_reason_code},
                    scope_json=scope.model_dump_json(),error_code=scope.denial_reason_code,question="")
                return
            self.db.transition(run_id,Status.SCOPE_GRANTED,"POLICY_RESOLVED",{**payload,"source_ids":list(scope.allowed_source_ids)},scope_json=scope.model_dump_json())
            self.db.transition(run_id,Status.RETRIEVING,"RETRIEVAL_STARTED")
            evidence = retrieval.retrieve(self.db,request.question,scope)
            with self.db.transaction() as cx:
                cx.executemany("INSERT INTO run_evidence VALUES (?,?)",[(run_id,item.chunk_id) for item in evidence])
                self.db.append_event(cx,run_id,"RETRIEVAL_COMPLETED",{"chunk_ids":[item.chunk_id for item in evidence],"count":len(evidence)})
                if any("SYSTEM:" in item.text for item in evidence):
                    self.db.append_event(cx,run_id,"UNTRUSTED_INSTRUCTION_DETECTED",{"note_code":"SOURCE_INSTRUCTIONS_HAVE_NO_AUTHORITY"})
            if not evidence:
                self.db.transition(run_id,Status.BLOCKED,"RUN_BLOCKED",{"reason_code":"EVIDENCE_EMPTY"},error_code="EVIDENCE_EMPTY")
                return
            with self.db.transaction() as cx:
                self.db.append_event(cx,run_id,"CONTEXT_ASSEMBLED",{"chunk_ids":[item.chunk_id for item in evidence],"prompt_hash":PROMPT_HASH,"prompt_version":"1.0"})
            self.db.transition(run_id,Status.DRAFTING,"DRAFTING_STARTED")
            # Fixture execution is not logged as a real provider/network invocation.
            event = "MODEL_REQUESTED" if request.mode == "live" else "FIXTURE_REQUESTED"
            with self.db.transaction() as cx:
                self.db.append_event(cx,run_id,event,{"mode":request.mode,"provider":"nebius" if request.mode == "live" else "fixture"})
            result = self.providers[request.mode].generate_draft(request=request,scope=scope,evidence=evidence)
            provider = dict(provider=result.provider,model_id=result.model_id,request_id=result.request_id,latency_ms=result.latency_ms,mode=request.mode,**result.metadata)
            self.db.transition(run_id,Status.EVALUATING,"MODEL_COMPLETED" if request.mode == "live" else "FIXTURE_COMPLETED",provider,provider_json=canonical(provider))
            try:
                draft = parse_draft(result.text)
            except (ValueError, TypeError, RecursionError):
                draft = None
            checks = evaluate(scope,evidence,draft,run_status=Status.EVALUATING)
            passed = all(check["passed"] for check in checks)
            target = Status.READY_FOR_REVIEW if passed else Status.BLOCKED
            with self.db.transaction() as cx:
                cx.executemany("INSERT INTO evaluation_results VALUES (?,?,?,?)",[(run_id,check["check_id"],int(check["passed"]),check["reason"]) for check in checks])
                self.db.append_event(cx,run_id,"EVALUATION_COMPLETED",{"checks":{item["check_id"]:item["passed"] for item in checks}})
                current = cx.execute("SELECT status FROM research_runs WHERE run_id=?",(run_id,)).fetchone()[0]
                if current != Status.EVALUATING:
                    raise ControlError("INVALID_TRANSITION")
                cx.execute("UPDATE research_runs SET status=?,draft_json=?,error_code=? WHERE run_id=?",
                    (target,draft.model_dump_json() if passed else None,None if passed else "EVALUATION_FAILED",run_id))
                self.db.append_event(cx,run_id,"READY_FOR_REVIEW" if passed else "RUN_BLOCKED",{"status":str(target)})
        except ModelUnavailable as error:
            code = str(error)
            self.db.transition(run_id,Status.MODEL_UNAVAILABLE,"MODEL_FAILED",{"reason_code":code},error_code=code)
        except Exception as error:
            # Never log exception messages, input text, headers, credentials or prompts.
            logger.warning("Run stopped: id=%s type=%s",run_id,type(error).__name__)
            code = str(error) if isinstance(error,ControlError) and str(error) in {"FIXTURE_SCENARIO_UNSUPPORTED","FIXTURE_INTEGRITY_FAILED","FIXTURE_EVIDENCE_MISMATCH","SCOPE_NOT_VALID","CONTEXT_OUT_OF_SCOPE"} else "CONTROL_FAILURE"
            try:
                self.db.transition(run_id,Status.BLOCKED,"RUN_BLOCKED",{"reason_code":code},error_code=code)
            except Exception:
                logger.error("Run could not append failure audit: id=%s",run_id)

    def recover_interrupted(self):
        rows = self.db.rows("SELECT run_id,status FROM research_runs")
        for row in rows:
            if row["status"] in {"RECEIVED","POLICY_EVALUATING","SCOPE_GRANTED","RETRIEVING","DRAFTING","EVALUATING"}:
                self.db.transition(row["run_id"],Status.BLOCKED,"RUN_BLOCKED",{"reason_code":"PROCESS_INTERRUPTED"},error_code="PROCESS_INTERRUPTED")

    def get(self, run_id, actor_id):
        row = self.db.one("SELECT * FROM research_runs WHERE run_id=?",(run_id,))
        if row is None:
            raise LookupError("RUN_NOT_FOUND")
        if actor_id not in {row["actor_id"],"alex_reviewer"}:
            raise PermissionError("RUN_NOT_AUTHORIZED")
        if not self.db.verify_chain(run_id):
            raise ControlError("AUDIT_INTEGRITY_FAILED")
        scope = json.loads(row.pop("scope_json")) if row["scope_json"] else None
        draft = json.loads(row.pop("draft_json")) if row["draft_json"] else None
        provider = json.loads(row.pop("provider_json")) if row["provider_json"] else None
        for name in ("scope_json","draft_json","provider_json"):
            row.pop(name,None)
        evidence = []
        if scope and scope["policy_decision"] == "ALLOW":
            evidence = self.db.rows("""SELECT c.*,s.title,s.classification,s.authority_tier,s.matter_id,s.version,s.url
                FROM run_evidence e JOIN source_chunks c USING(chunk_id) JOIN sources s USING(source_id)
                WHERE e.run_id=? AND s.classification != 'RESTRICTED_PRIVILEGED' ORDER BY s.source_id,c.chunk_id""",(run_id,))
            allowed = set(scope["allowed_source_ids"])
            if any(item["source_id"] not in allowed or hashlib.sha256(item["text"].encode()).hexdigest() != item["content_hash"] for item in evidence):
                raise ControlError("EVIDENCE_INTEGRITY_FAILED")
        checks = self.db.rows("SELECT check_id,passed,reason FROM evaluation_results WHERE run_id=? ORDER BY rowid",(run_id,))
        review = self.db.one("SELECT actor_id,decision,rationale,created_at FROM review_decisions WHERE run_id=?",(run_id,))
        if row["status"] not in {"READY_FOR_REVIEW","APPROVED","REJECTED","REVISION_REQUESTED"}:
            draft = None
        return {**row,"scope":scope,"draft":draft,"provider":provider,"evidence":evidence,"checks":checks,
            "review":review,"audit":self.db.rows("SELECT * FROM audit_events WHERE run_id=? ORDER BY sequence_number",(run_id,)),"audit_valid":True}
