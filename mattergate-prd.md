# Product Requirements Document — MatterGate

**PRD revision:** 2.0, October 24, 2026
**Application release:** 0.2.0 — Evidence & Review
**Status:** Implemented local demonstration; automated and operator-guided acceptance recorded; publication/submission work remains.

This PRD describes current requirements and implemented behavior. It supersedes the original build-ready proposal. [HANDOVER.md](HANDOVER.md) explains the product and the reasons behind the decisions.

## 1. Product definition

MatterGate is a permissioned legal/privacy research workflow. It determines the requester's research scope before retrieving evidence or calling an NVIDIA model through Nebius Token Factory. It presents a cited draft only after structural controls pass, requires a separate human disposition, and preserves a readable receipt and ordered audit record.

**Product line:** Permissioned legal research—policy before model context.

The application owns authorization, retrieval, evaluation, state transitions and audit writes. The model drafts within supplied context. The human reviews the assessment. Approval of a research draft does not authorize the underlying business action.

## 2. Problem and intended users

The product addresses four concerns in sensitive research: unauthorized source context, statements that are difficult to trace, draft results that appear automatically approved, and retrieved text that attempts to override instructions.

| Persona | Intended need | Implemented demo role |
|---|---|---|
| Privacy counsel, Maya | Inspect a bounded research assessment and its sources | Supported vendor-risk requester |
| Operations requester, Jordan | Ask a vendor question without access to restricted matters | Supported requester; restricted M&A denied |
| Human reviewer, Alex | Judge the research draft and record a reasoned disposition | Review role; cannot draft through the supported policy |
| Legal operations/governance lead, Priya | Inspect permission, evidence, model usage and responsibility | Product persona, not a separate implemented identity |

These are product hypotheses. One operator's walkthrough and technical verification do not constitute target-customer research or measured business impact.

## 3. Goals and success evidence

| ID | Goal | Current acceptance |
|---|---|---|
| G1 | Authorization before context | Automated and isolated-browser denial checks; no retrieval/provider invocation when denied |
| G2 | Useful, concise cited draft | Live structured brief demonstrated; substantive/legal usefulness still needs target-role validation |
| G3 | Genuine visible Nebius/NVIDIA use | Operator live receipt identifies model, HTTP/finish status, request ID, tokens and latency |
| G4 | Inspectable evidence and responsibility | Inline references, source details, review record and downloadable receipt |
| G5 | Predictable, honest demonstration | Exact offline fixture, explicit mode labels and safe provider failure |
| G6 | Readable coherent workflow | Responsive browser checks, guidance, history filters and operator-confirmed native 200% form zoom |
| G7 | Reproducible handoff | Source, pinned dependencies, setup, tests, licenses, attribution and source archive tooling |

Acceptance evidence is dated in [testing](docs/testing.md). Do not convert a single live run into a reliability percentage or legal-quality claim.

## 4. Scope

### Included

- Fixed demo identities, supported matters, purposes and jurisdictions.
- Explicit permission scope and authorization-filtered local retrieval.
- Curated synthetic/public corpus with chunk identifiers and content hashes.
- Live Nebius inference and a distinct exact-scenario offline fixture.
- Strict statement-owned citations and ten structural controls.
- Human review, immutable dispositions and rationale.
- State guidance, inline evidence inspection, history filters and readable layouts.
- Safe diagnostics, instrumented attempts, audit chain and JSON receipt export.
- Source test-build packaging and public-repository documentation.

### Outside release 0.2.0

Real client documents, arbitrary upload/URL ingestion, SSO, production role administration, open-web research, vector database infrastructure, autonomous actions, linked revision regeneration, production deployment qualification, externally anchored audit integrity and legal/compliance certification are not implemented.

The local role selector is a simulation. A server-checked signed session prevents trusting a posted actor alone; it does not authenticate a real user.

## 5. Core scenarios

### S1 — Allowed EU vendor assessment

Jordan asks the exact seeded question:

> Can our sales team share EU customer contact data with Vendor X so it can triage support tickets?

The application resolves an allowed vendor-risk scope, selects at most five authorized chunks, generates a bounded brief and evaluates it. Passing output reaches `READY_FOR_REVIEW`. Alex may approve, reject or request revision.

Live recommendations may vary. They must remain one of the defined enums and must not grant application approval.

### S2 — Restricted M&A request

The request uses matter `restricted_m_and_a` and purpose `transaction_analysis`. Jordan and Maya are denied in this release.

Expected: `DENIED` before retrieval or inference; no restricted source title, ID, excerpt or corpus count appears in the denial view/export. The denied question is cleared from the run record. Instrumented new runs report zero retrieval/provider attempts.

### S3 — Untrusted source instruction

An authorized synthetic reference contains instruction-like text. It is escaped and placed inside a fixed untrusted evidence envelope. It cannot expand scope, define tools or submit a review. An instruction-detection audit event is separate from the output checks.

The known prohibited-output string rules must block defined attack/approval statements, including quotations. Passing them does not prove general prompt-injection resistance.

### S4 — Unsupported custom fixture

A custom question in fixture mode, such as the tested two-year-retention question, must stop with `FIXTURE_SCENARIO_UNSUPPORTED` and explain that the fixture supports only the exact seeded EU question.

This is an offline-scenario failure after permission/retrieval, not a policy denial. No live model call is made. The original approved run is unchanged.

### S5 — Provider failure

Configuration, authentication, rate-limit, timeout, incomplete-output and response-format failures must produce safe differentiated guidance. A failed live execution must never silently become a fixture or different model.

**Start separate fixture demo** may appear after a live provider failure only. It creates a different allowed seeded run and is not offered as a denial/output-control bypass.

## 6. Experience and screen requirements

| Screen | Route | Required behavior |
|---|---|---|
| Overview | `/` | Explain the workflow; launch allowed/denied scenarios; show identity-scoped history |
| New research | `/runs/new` | Collect request dimensions, plain-text question and explicit execution mode |
| Progress | `/runs/{id}` | Show actual ordered stages, state-specific guidance and valid next action |
| Brief | `/runs/{id}/brief` | Summary, conditions, caveats, questions and references beside material statements |
| Human review | `/runs/{id}/review` | Reviewer switch, recommendation context, rationale and permitted dispositions |
| Run receipt | `/runs/{id}/audit` | Human-readable outcome, diagnostics, measured counters and expandable audit events |
| System status | `/status` | Distinguish configuration from recorded live completion; explain PriviLAB reuse |
| Receipt download | `/api/runs/{id}/receipt` | Recheck read/integrity access and return allowlisted JSON |

### Input requirements

- Requester must match the signed demo session; identities are Jordan, Maya or Alex.
- Matters: `vendor_onboarding`, `restricted_m_and_a`.
- Purposes: `vendor_risk_assessment`, `support_operations`, `transaction_analysis`.
- Jurisdictions: `EU`, `US`, `GLOBAL`.
- Plain-text question: 20–1,000 characters, without markup/control characters.
- Mode: `fixture` or `live`. Live is selectable only when server settings are configured.
- Supported research remains vendor onboarding plus vendor risk assessment for Jordan/Maya. Other combinations fail closed under the small policy.
- Fixture success additionally requires its exact seeded EU request and expected evidence.

### Evidence and review interaction

Every summary, condition and caveat must have adjacent references derived from its accepted exact claim mapping. A reference opens/focuses the selected excerpt and exposes a return link. Do not infer references from similar wording.

Source details show classification, authority tier, version and provenance. Technical hashes and JSON may be expanded as needed.

The review panel must state that passing checks does not establish source support or legal accuracy. Approval accepts the research assessment, including a possible `DO_NOT_PROCEED` recommendation.

### Readability and history

Use a consistent type scale: normally 16px content, 14px controls/support and at least 12px nonessential metadata. Avoid blanket font enlargement. Status must use text in addition to color; interactive focus must be visible.

Support the tested 1440/1024/768/390 CSS-pixel widths without page-wide overflow and retain form usability at native 200% zoom. A real mobile device and comprehensive accessibility audit remain separate qualification.

History filters are All runs, Needs review, Reviewed and Stopped. Apply them after requester/reviewer read permissions. Keep timestamps, mode and short run IDs visible; filtering must not delete history.

## 7. Functional requirements

| ID | Requirement | Acceptance rule |
|---|---|---|
| FR-1 | Resolve policy before retrieval | Only an effective allow can proceed; source scope binds run, actor, matter, purpose, jurisdiction, policy version, actions and expiry |
| FR-2 | Preserve curated chunk provenance | Each selected chunk has a source ID and verifiable content hash; no real client data |
| FR-3 | Scope retrieval | Intersect explicit source IDs with source metadata; max five chunks/8,000 context characters; stable scoped ranking |
| FR-4 | Bound Nebius generation | Approved HTTPS endpoint, NVIDIA model, TLS, no redirects/proxy routing, total deadline ≤45 seconds, output cap ≤900 tokens, response cap 100KB, at most two generation attempts |
| FR-5 | Strict structured result | Reject malformed/duplicate/extra fields, unknown references and size violations; retain exact statement text |
| FR-6 | Apply structural controls | All ten checks pass before a reviewable brief is rendered |
| FR-7 | Enforce human review | Only Alex, only from Ready for review, one disposition; reject/revise require rationale; state/decision/audit write atomically |
| FR-8 | Preserve safe audit | Ordered append-only events and local chained hashes; no prompts, source bodies, credentials or rationale in event payloads |
| FR-9 | Fail safely | Denied/blocked/unavailable results show safe explanation and no generated reviewable brief; interrupted work blocks on restart |
| FR-10 | Keep workflow understandable | Distinct state guidance, accessible controls, exact inline evidence and clear recommendation/disposition labels |
| FR-11 | Export safe receipt | Same owner/Alex read and integrity gate as the run; explicit allowlist; no question, excerpts, prompts, credentials or rationale |
| FR-12 | Measure provider operations honestly | Count instrumented transport entries including regeneration; legacy unknown counts remain null/Not recorded |
| FR-13 | Explain provider execution | Validate status/finish/ID/token/latency metadata; failed diagnostics cannot imply a completed live generation |

These are product requirements for this local demonstration, not production certifications.

## 8. Draft contract and structural controls

### Provider wire contract

Each material statement owns its chunk references:

~~~json
{
  "summary": {"claim": "A bounded statement.", "chunk_ids": ["AUTHORIZED-CHUNK-ID"]},
  "recommendation": "INSUFFICIENT_EVIDENCE",
  "conditions": [],
  "risks_and_caveats": [],
  "open_questions": ["What information is missing?"],
  "disclaimer": "MatterGate is a demonstration research workflow using synthetic and public materials. It does not provide legal advice, make legal decisions, or establish compliance."
}
~~~

The recommendation enum also permits `PROCEED_WITH_CONDITIONS` and `DO_NOT_PROCEED`. Live wire limits are at most two conditions, one caveat and two open questions. Material statements use the same cited-statement shape as the summary.

The application projects these unchanged claims into the public `Draft` contract: summary/condition/caveat strings plus a citation list. Legacy public-format fixtures remain supported with independent exact coverage validation. Public serialization is bounded to 6,000 characters; the parser rejects oversized raw input above 12,000 characters. Full field limits are in [domain.py](app/domain.py) and [API documentation](docs/api.md).

### Required checks

| Check | What it establishes |
|---|---|
| `POLICY_ALLOW` | Active permitted scope and selected-source membership |
| `EVIDENCE_NONEMPTY` | Authorized evidence exists |
| `OUTPUT_SCHEMA` | Strict draft contract parsed |
| `CITATION_PRESENT` | At least one reference exists |
| `CITATION_IN_SCOPE` | Exact references resolve inside selected evidence |
| `CLAIM_COVERAGE` | Summary/condition/caveat text has exact linked claims |
| `DISCLAIMER_EXACT` | Required disclosure matches |
| `NO_RESTRICTED_SOURCE` | Defined restricted classification/IDs/canary are absent |
| `NO_UNTRUSTED_COMMAND_FOLLOWING` | Known prohibited command/approval patterns are absent |
| `REVIEW_REQUIRED` | Application evaluation state precedes human disposition |

These checks establish structural boundaries and linkage. A cited statement can still overstate or misinterpret its evidence. Human source-support review is required; open questions are not treated as supported factual conclusions.

## 9. Integration and architecture requirements

### Nebius

Current working configuration is `https://api.tokenfactory.nebius.com/v1` with `nvidia/Nemotron-3_5-Lightning`. Thinking is disabled for the recognized model configuration to preserve the bounded output budget for the JSON brief.

Nebius Token Factory performs runtime inference. The FastAPI application runs locally. Do not claim a Nebius AI Cloud compute deployment.

### PriviLAB

Reuse selected attributed code from pinned commit `21baa4ccdc468bd6a30681344eb8ec3df752790a` through local source adaptations. The permission evaluator, scoped retrieval and citation checks must execute in both live and fixture paths.

There is no separate PriviLAB service or API connection. Keep Apache-2.0 notices, modification information and the [source manifest](docs/upstream/privilab-manifest.json). MatterGate's independently written Nebius adapter must not inherit an upstream provider merely by changing its base URL.

### Local implementation

Python/FastAPI/Pydantic own routes and contracts; Jinja/minimal JavaScript provide the interface; SQLite/FTS5 provide storage and search; HTTPX provides bounded transport.

Main tables are users, policies, sources, source_chunks, research_runs, run_evidence, evaluation_results, review_decisions and audit_events. Evaluation results use `(run_id, check_id)` as their key. Review decisions are unique per run. FTS is a local index.

The observability upgrade adds audit metadata without a schema migration. Do not rewrite historical audit bytes to fabricate new counters.

## 10. State machine and API contract

~~~text
RECEIVED → POLICY_EVALUATING → DENIED
                           → SCOPE_GRANTED → RETRIEVING → DRAFTING → EVALUATING
                                                                    → BLOCKED
                                                                    → READY_FOR_REVIEW
                                                                       → APPROVED
                                                                       → REJECTED
                                                                       → REVISION_REQUESTED
~~~

Drafting provider failures use `MODEL_UNAVAILABLE`. Active stages may block on control/system failure; interrupted active runs become `BLOCKED`. `CONTEXT_ASSEMBLED` is an audit event, not a persisted status. Valid transitions are fixed in application code.

| Endpoint | Contract |
|---|---|
| `GET /api/session` | Initialize/read signed demo session and CSRF token |
| `POST /api/session` | Explicit demo identity switch; rotate CSRF |
| `POST /api/runs` | Validate session/request/rate/configuration; return HTTP 202 with run ID and URLs; background execution follows |
| `GET /api/runs/{id}` | Original requester or Alex; integrity-gated safe run, permitted evidence, controls and disposition |
| `POST /api/runs/{id}/review` | Alex-only server state transition; 403 unauthorized, 409 unavailable/conflict, 422 missing required rationale |
| `GET /api/runs/{id}/receipt` | Authorized JSON attachment, versioned safe receipt |
| `GET /api/status` | Safe configuration and recorded live-completion indicators; no credentials |

Run creation does not synchronously return Ready for review or Denied. Clients poll the status URL. Configuration alone does not prove a successful provider call.

## 11. Security, privacy and evidence requirements

- Keep private keys/session secrets in server configuration and out of Git.
- Retain signed demo sessions, CSRF/origin checks, bounded input/rate limits, HTML escaping and CSP.
- Escape evidence delimiters; embedded role labels remain data, not executable instructions.
- Scope-constrained evidence is sent to the remote model in live mode. Safe audit logging does not mean inference data stays local.
- Store only synthetic/public demonstration materials. Local questions, accepted drafts and reviewer rationale are persisted; logs/exports have narrower fields.
- Validate diagnostics with strict enum/format/integer bounds; never expose raw provider bodies or exception text.
- Verify source hashes and the local audit chain before serving run/receipt records.
- Explain that the local chain is unanchored and can be rewritten by a sufficiently privileged administrator.
- Preserve prior decisions and fail safely on persistence/integrity errors.
- Source packaging must exclude secrets, databases, caches, logs, generated artifacts and the local planning directory.
- Do not expose a freely selectable-identity demo with uncontrolled paid inference as a production service.

## 12. Verification status

| Evidence | Status |
|---|---|
| Automated regression suite | 101 passed on the implemented 0.2.0 source |
| Isolated fixture browser workflow | Passed: evidence navigation, review, receipt download, identity return and denial |
| Layout checks | 32 screen/viewport checks passed |
| Extracted source build | 101 passed with the existing pinned environment; not a fresh dependency installation |
| Updated live run | Operator confirmed `08126a78`: HTTP 200, stop, 1,678 input/302 output tokens, 1,515ms provider latency, one retrieval/transport attempt, 10/10 controls and draft approval |
| Inline evidence, receipt download and filters | Operator confirmed working |
| Unsupported custom fixture guidance | Operator screenshot confirmed `FIXTURE_SCENARIO_UNSUPPORTED`, run `caf19e58` |
| Native 200% request-form zoom | Operator confirmed readable with no overlap |
| Multiple live trials, real mobile device, target-role study, current remote CI | Not established by this acceptance session |

Use [testing](docs/testing.md) for detailed qualifications. Do not imply all reliability, accessibility or legal-quality questions are closed.

## 13. Definition of done

### Local product milestone

Implemented policy-before-context flow, live/fixture separation, strict cited output, structural controls, human disposition, failure guidance, readable evidence UI, receipts/history, attribution and reproducible source packaging. Automated results and the operator's current live walkthrough support this milestone.

Documentation updates after archive generation require rebuilding the archive. The old archive manifest does not cover this revised PRD or handover.

### Submission milestone — still open

- Confirm and publish the intended source revision; inspect CI for it.
- Provide a working judge-accessible demo/test-build URL and usable access instructions.
- Record and publish the demonstration video; complete the form and actual tool feedback.
- Recheck official submission requirements before filing.
- Accurately describe original work, PriviLAB reuse, runtime NVIDIA/Nebius use and limitations.

Repository publication is not deployment. A local archive is not an uploaded judge-access link.

### Future product qualification

Target-user usefulness, substantive source-support assessment, repeated live reliability, true authentication, document administration, durable jobs, deployment isolation, cost/retention controls and appropriate operational/security review require separate work.

## 14. Version history and references

Revision 1.0 was the original build-ready proposal. Revision 2.0 replaces proposed layouts/API examples with implemented behavior, records actual source reuse, explains statement-owned citations and the Evidence & Review upgrade, and separates verified results from pending qualification.

- [Product/engineering handover](HANDOVER.md)
- [Current verification](docs/testing.md)
- [Architecture](docs/architecture.md), [API](docs/api.md), [threat model](docs/threat-model.md)
- [PriviLAB assessment and pinned sources](docs/privilab-reuse.md)
- [Official hackathon rules](https://nebiusglobalaihackathon.devpost.com/rules)
- [Organizer submission guidance](https://nebiusglobalaihackathon.devpost.com/updates/46205-how-to-build-a-winning-project)

External requirements and model availability should be rechecked before submission or deployment.
