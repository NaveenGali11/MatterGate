# API contract

The same-origin web UI is the supported entry point. The backend is authoritative
for scope, state, review identity and decisions. FastAPI's interactive docs and
ReDoc pages are disabled; OpenAPI JSON remains available at `/openapi.json`.

Examples below use synthetic data. They are documentation, not an executed API test.

## Session and CSRF

`GET /api/session` initializes a signed demo session and returns:

~~~json
{
  "actor_id": "jordan_sales_ops",
  "csrf_token": "<session-token>",
  "users": {
    "jordan_sales_ops": {"name": "Jordan", "role": "Sales Operations", "initials": "JO"},
    "maya_privacy_counsel": {"name": "Maya", "role": "Privacy Counsel", "initials": "MA"},
    "alex_reviewer": {"name": "Alex", "role": "Human Reviewer", "initials": "AL"}
  }
}
~~~

Maintain the session cookie. For every POST, send JSON, the current
`X-CSRF-Token` header, and the same-origin request. If an Origin header is present,
it must match the app origin.

`POST /api/session` switches the explicitly simulated demo identity:

~~~json
{"actor_id": "alex_reviewer"}
~~~

The response includes a new `csrf_token`; replace the old token before the next
mutation. The endpoint does not authenticate a real person. Do not publish session
cookies or CSRF tokens as testing credentials.

## Create a run

`POST /api/runs`:

~~~json
{
  "actor_id": "jordan_sales_ops",
  "matter_id": "vendor_onboarding",
  "jurisdiction": "EU",
  "purpose": "vendor_risk_assessment",
  "question": "Can our sales team share EU customer contact data with Vendor X so it can triage support tickets?",
  "mode": "live"
}
~~~

The actor must match the session. Allowed matter IDs are `vendor_onboarding` and
`restricted_m_and_a`; jurisdictions are `EU`, `US` and `GLOBAL`. Purposes are
`vendor_risk_assessment`, `support_operations` and `transaction_analysis`.
Being an allowed input enum does not mean policy permits that combination.

Questions contain 20–1,000 plain-text characters; markup/control characters are
rejected. Mode is `live` or `fixture`, defaulting to fixture at the API level.
The UI uses configuration to choose its default mode.

Returns **202 Accepted** after creation, before background execution completes:

~~~json
{
  "run_id": "<server-generated-uuid>",
  "status": "RECEIVED",
  "status_url": "/api/runs/<id>",
  "brief_url": "/runs/<id>/brief",
  "audit_url": "/runs/<id>/audit"
}
~~~

The API limits run creation to six requests per session per minute in this single
process. Live creation is rejected if configuration is not ready.

## Read a run

`GET /api/runs/{run_id}` returns the safe run projection: status, synthetic request,
scope snapshot, selected evidence, control results, provider metadata, review and
ordered audit events. The original requester and Alex may read it.

A draft is exposed only for ready or reviewed runs. Denied runs have no evidence
and their persisted question is cleared. Blocked drafts are not returned.
Integrity failures produce a safe error rather than an approved/completed result.

Evidence includes source/chunk IDs, title, authorized excerpt, classification,
authority tier, source version and content hash. Provider metadata includes actual
provider/model, mode, latency, attempt count, request ID when available, and fixture
identity/hash when applicable.

`live_verified` on system status only indicates a stored completed Nebius
generation exists. It is not proof that every evaluation passed; inspect that run.

## Review

`POST /api/runs/{run_id}/review`:

~~~json
{
  "actor_id": "alex_reviewer",
  "decision": "APPROVE",
  "rationale": "Reviewed the synthetic research draft and its citations."
}
~~~

Decisions are `APPROVE`, `REJECT` and `REQUEST_REVISION`. Only Alex's session may
submit. Reject/revision need a nonblank rationale; the rationale is limited to
1,000 characters. The run must be `READY_FOR_REVIEW` with all required checks passed.

~~~json
{"run_id": "<id>", "status": "APPROVED"}
~~~

Repeated decisions conflict. The review, state update and safe audit event commit
in one transaction. A review of the draft is not authorization to act on the
underlying business question.

## Status

`GET /api/status` reports demo mode, configuration-derived provider mode,
configured model ID, database readiness, seed version, `live_configured`,
`live_verified` and pinned upstream revision. It never returns API keys, session
secrets, raw environment settings or credentials in the endpoint.

## Provider wire format and public brief

Live inference is prompted for statement-owned citations:

~~~json
{
  "summary": {
    "claim": "This synthetic assessment requires a signed DPA before sharing.",
    "chunk_ids": ["INT-DPA-001-C01"]
  },
  "recommendation": "DO_NOT_PROCEED",
  "conditions": [
    {
      "claim": "Confirm the support-only purpose before sharing.",
      "chunk_ids": ["INT-DPA-001-C01"]
    }
  ],
  "risks_and_caveats": [
    {
      "claim": "International transfer safeguards remain unresolved in the synthetic DPA.",
      "chunk_ids": ["INT-DPA-001-C01"]
    }
  ],
  "open_questions": ["Has the synthetic DPA been signed?"],
  "disclaimer": "<exact server-supplied disclosure>"
}
~~~

This illustrates shape, not a recorded model answer. `CitedDraft` allows at most
two conditions, one caveat and two questions. Each statement has 1–5 chunk IDs.
The server projects claims unchanged into the public `Draft` fields: string
summary, string condition/caveat lists, and matching `citations` entries. The
original public/fixture contract remains supported and is subject to the same
coverage check.

Only enum recommendations are accepted. Duplicate/unexpected JSON fields, missing
citation data, invalid types and a serialized public draft over 6,000 characters
are rejected. A claim is at most 1,000 characters; the summary is at most 900.
A public draft requires 1–5 citations, and each condition/caveat/question item
is bounded. The input response string is capped before parsing. Validation does
not establish factual correctness.

## Common HTTP outcomes

| HTTP | Meaning |
|---|---|
| 200 | Status/read/review/identity operation succeeded |
| 202 | Research run created and queued |
| 403 | Session actor, read permission, reviewer or CSRF/origin mismatch |
| 404 | Run or page not found |
| 409 | Review unavailable or already decided |
| 422 | Invalid input, unsupported live configuration or missing required rationale |
| 429 | Local session request limit |
| 503 | Safe persistence or control-integrity failure |

A provider or evaluation failure usually appears in a persisted run state rather
than as a failed initial POST. Poll the run and inspect its reason/checks.
