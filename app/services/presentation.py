"""Human-readable run guidance and safe views of existing accepted records."""
import json

STATE_GUIDANCE = {
    "RECEIVED": ("Request received", "The application will check your permission before reading evidence.", "Follow progress", "progress"),
    "POLICY_EVALUATING": ("Checking permission", "Your identity, matter, purpose and jurisdiction determine the research scope.", "Follow progress", "progress"),
    "SCOPE_GRANTED": ("Research permission granted", "Only the sources in this scope can enter the draft context.", "Follow progress", "progress"),
    "RETRIEVING": ("Selecting authorized evidence", "The application is retrieving excerpts inside the granted scope.", "Follow progress", "progress"),
    "DRAFTING": ("Drafting from evidence", "Generation is bounded. Model output cannot change permissions or approve this request.", "Follow progress", "progress"),
    "EVALUATING": ("Checking the draft", "Citation linkage and output controls must pass before a person can review it.", "Follow progress", "progress"),
    "READY_FOR_REVIEW": ("Your draft is ready to inspect", "Structural checks passed. Review source support and missing facts before recording a decision.", "Inspect the brief", "brief"),
    "APPROVED": ("Research draft approved", "Alex accepted this research assessment. This does not authorize data sharing or other business action.", "View review decision", "review"),
    "REJECTED": ("Research draft rejected", "The reviewer declined this assessment. The decision and rationale are preserved.", "View review decision", "review"),
    "REVISION_REQUESTED": ("Revision requested", "Read the reviewer's rationale, then start a new research run. The original decision remains unchanged.", "View revision request", "review"),
    "DENIED": ("Research permission denied", "This identity is not permitted to research the requested matter or source category. No answer was generated.", "View the run receipt", "audit"),
    "BLOCKED": ("Draft withheld by controls", "The run could not satisfy the required controls. Its generated content is not available for review.", "Inspect failed controls", "progress"),
    "MODEL_UNAVAILABLE": ("Generation could not complete", "The provider did not return an acceptable complete draft. No research answer is available.", "View safe diagnostics", "audit"),
}
ERROR_GUIDANCE = {
    "PUBLIC_LIVE_QUOTA_REACHED": "The public demo's live allowance has been reached. You can start a separate seeded fixture demo without an AI call.",
    "PUBLIC_LIVE_DISABLED": "Live generation is temporarily paused. You can still use the seeded fixture demo.",
    "PUBLIC_SERVER_BUSY": "The public demo is serving other live requests. Wait briefly, then start a new run, or choose fixture mode.",
    "PROVIDER_AUTH_ERROR": "Nebius rejected authentication. Check the server's API key and account access, then start a new run.",
    "PROVIDER_RATE_LIMITED": "Nebius rate-limited this request. Wait before explicitly starting a new run.",
    "PROVIDER_HTTP_ERROR": "Nebius returned an unsuccessful HTTP status. Check provider availability and account access.",
    "PROVIDER_TIMEOUT": "The total generation deadline expired. Check provider availability before starting a new run.",
    "PROVIDER_INCOMPLETE_OUTPUT": "Generation stopped before a complete response, possibly at the output-token limit. The partial output is withheld.",
    "PROVIDER_NOT_CONFIGURED": "Live inference is not configured. Configure Nebius on the server or start a separate seeded fixture demo.",
    "PROVIDER_INVALID_RESPONSE": "The provider response could not be accepted. Check endpoint and model compatibility.",
    "PROVIDER_RESPONSE_LIMIT": "The provider response exceeded the application's bounded response limit.",
    "PROCESS_INTERRUPTED": "The server restarted during this run. Start a new run; this record is preserved.",
    "FIXTURE_SCENARIO_UNSUPPORTED": "The fixture supports only the exact seeded EU vendor question. Use that scenario, or live mode for a custom question.",
    "EVIDENCE_EMPTY": "No usable evidence was retrieved within this scope. Check the question and supported scenario.",
    "EVALUATION_FAILED": "One or more structural controls failed. Inspect the reasons below; changing to a fixture cannot bypass these controls.",
}


def guidance(run):
    title, detail, action, tab = STATE_GUIDANCE[run["status"]]
    return {"title":title,"detail":detail,"action":action,"tab":tab,
            "resolution":ERROR_GUIDANCE.get(run.get("error_code")),
            "failed_checks":[check for check in run["checks"] if not check["passed"]]}


def evidence_view(run):
    """Exact accepted claim mapping; never infer links from similarity."""
    draft = run.get("draft")
    if not draft:
        return {"sections":[],"sources":[]}
    normalize = lambda text: " ".join(text.split()).casefold()
    evidence = {item["chunk_id"]:item for item in run["evidence"]}
    ordered = list(evidence)
    links = {}
    for citation in draft["citations"]:
        values = links.setdefault(normalize(citation["claim"]), [])
        for cid in citation["chunk_ids"]:
            if cid in evidence and cid not in values:
                values.append(cid)
    sections = []
    for label, statements in [("Summary",[draft["summary"]]),("Conditions to address",draft["conditions"]),
                               ("Risks & caveats",draft["risks_and_caveats"])]:
        sections.append({"label":label,"statements":[{"text":text,"anchor":f"claim-{len(sections)}-{i}",
            "refs":[{"chunk_id":cid,"number":ordered.index(cid)+1,"title":evidence[cid]["title"]}
                    for cid in links.get(normalize(text), [])]} for i,text in enumerate(statements)]})
    return {"sections":sections,"sources":list(evidence.values())}


def receipt(run):
    """Versioned export allowlist. Deliberately excludes question, excerpts and rationale."""
    events = [{"type":event["event_type"],"payload":json.loads(event["safe_payload_json"])} for event in run["audit"]]
    created = next((e["payload"] for e in events if e["type"] == "RUN_CREATED"), {})
    instrumented = created.get("instrumentation_version") == 1
    retrieval_calls = sum(e["type"] == "RETRIEVAL_STARTED" for e in events) if instrumented else None
    attempts = sum(e["type"] == "TRANSPORT_ATTEMPTED" for e in events) if instrumented and created.get("transport_observed") else None
    scope, provider, review = run.get("scope") or {}, run.get("provider") or {}, run.get("review") or {}
    denied = run["status"] == "DENIED"
    return {
        "receipt_version":"1.0","run_id":run["run_id"],"created_at":run["created_at"],
        "actor_id":run["actor_id"],"matter_id":run["matter_id"],"purpose":run["purpose"],
        "jurisdiction":run["jurisdiction"],"mode":run["mode"],"status":run["status"],
        "permission":scope.get("policy_decision","NOT_RECORDED"),"policy_version":scope.get("policy_version"),
        "evidence_count":None if denied else len(run["evidence"]),
        "retrieval_attempts":retrieval_calls,"provider_attempts":attempts,
        "provider_completed":any(e["type"] == "MODEL_COMPLETED" for e in events),
        "provider":{key:provider[key] for key in ("provider","model_id","request_id","latency_ms","attempt",
                    "http_status","finish_reason","input_tokens","output_tokens","outcome") if key in provider},
        "checks_passed":sum(bool(item["passed"]) for item in run["checks"]),"checks_total":len(run["checks"]),
        "review":{key:review[key] for key in ("actor_id","decision","created_at") if key in review},
        "audit_valid":bool(run["audit_valid"]),"audit_events":len(events),
        "audit_head":run["audit"][-1]["event_hash"] if run["audit"] else None,
        "limits":"Citation linkage is structural; source support requires human review. Hash verification checks a local, unanchored chain. Draft approval does not authorize business action.",
    }
