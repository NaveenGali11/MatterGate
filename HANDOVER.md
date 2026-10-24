# MatterGate — product and engineering handover

Updated October 24, 2026 · Application version 0.2.0 · PRD revision 2.0

**Start here:** this document explains the product, the reasoning behind it, what works today, and what the next owner needs to do. The [PRD](mattergate-prd.md) defines current requirements; the [documentation index](docs/README.md) links the detailed technical guides.

## 1. What the product does

MatterGate helps a requester prepare a short legal/privacy research assessment from evidence the application permits them to use. It checks research permission before retrieving documents or sending context to an NVIDIA model through Nebius Token Factory.

The model drafts a summary, conditions, caveats and questions for counsel. Application code then checks the structure, citations and defined restrictions. A human reviewer decides whether to approve the research draft, reject it or request revision. A run receipt explains what happened and preserves an ordered audit trail.

The central distinction is responsibility:

| Decision | Owner | Meaning |
|---|---|---|
| May this requester research this matter for this purpose? | Application policy | Determines whether research can begin and which sources are eligible |
| What assessment follows from the supplied excerpts? | NVIDIA model, subject to controls and human inspection | Produces a draft recommendation |
| Is this research assessment acceptable? | Human reviewer, Alex in the demo | Records a disposition of the draft |
| May the business actually share data? | Outside this demonstration | Never granted by a MatterGate review button |

An approved draft can recommend **do not proceed**. Approving that assessment does not authorize data sharing.

## 2. Why we built it

The target problem is evidence-heavy research where access and accountability matter. A useful research assistant must help a reviewer answer three questions: “Was this requester permitted to use these sources?”, “What supports this statement?”, and “Who reviewed the result?”

The product makes that chain visible. Its purpose is to assist research while keeping authorization, source selection and approval in application code and human hands.

The PRD identifies legal counsel, privacy teams, operations requesters and legal operations/governance leads as likely users. These are intended personas, not validated customers. We have an operator walkthrough and technical tests; we have not established market demand, measured time savings or validated legal quality with a customer study.

## 3. A concrete example

Jordan in Sales Operations asks:

> Can our sales team share EU customer contact data with Vendor X so it can triage support tickets?

The application permits research within the supported vendor-risk scope. It selects authorized excerpts from synthetic internal policies, a draft DPA and an attributed public reference. Nebius runs the configured NVIDIA model on that bounded context.

The resulting draft may say that a signed DPA, vendor review and minimum necessary fields are required. Numbered references let the reviewer inspect the exact selected excerpt beside each material statement.

The structural checks must pass before Alex can submit a review. The final receipt records the permission outcome, selected evidence, provider execution, checks and human disposition.

A restricted M&A request takes a different path: policy denies it before retrieval or inference. A denied request does not reveal restricted document titles, identifiers or excerpts.

## 4. The workflow

~~~mermaid
flowchart TD
    Request[Identity, matter, purpose, jurisdiction and question] --> Permission{Application policy}
    Permission -->|Deny| Denial[Safe denial and audit record]
    Permission -->|Allow| Evidence[Retrieve only scoped evidence]
    Evidence --> Generate[Draft via NVIDIA model on Nebius]
    Generate --> Controls{Parse and structural checks}
    Generate -->|Provider failure| Failure[Safe diagnostics; no brief]
    Controls -->|Fail| Block[Withhold draft and explain]
    Controls -->|Pass| Review[Ready for human review]
    Review --> Decision[Approve draft / Reject / Request revision]
    Decision --> Receipt[Run receipt and audit trail]
~~~

A **run** is one execution with its own ID and history. Starting a fixture demo or another question creates a new run. Existing decisions are preserved.

## 5. What is implemented

| Capability | Current behavior |
|---|---|
| Demo identities | Jordan and Maya can request supported vendor research; Alex can review. Identities are freely selectable demonstrations, not real login |
| Policy boundary | Fixed actor/matter/purpose/jurisdiction policy resolves an explicit, expiring source scope |
| Retrieval | SQLite FTS5, source-ID and metadata filtering, at most five chunks and 8,000 context characters |
| Live generation | NVIDIA Nemotron 3.5 Lightning via the Nebius Token Factory chat-completions API |
| Offline fixture | Hash-checked saved result for the exact seeded EU vendor question |
| Draft contract | Strict JSON; material statements own their chunk references |
| Evaluation | Ten deterministic structural checks; any failed check blocks the reviewable brief |
| Evidence review | References beside statements, authorized excerpts, provenance details and return-to-claim navigation |
| Human decisions | Alex-only server validation; one immutable decision; rationale required for rejection or revision |
| Receipt and audit | Readable summary, measured attempts for new runs, expandable events and local hash-chain verification |
| Export | Permission-checked JSON receipt with an explicit safe field allowlist |
| History | Identity-scoped ledger, execution mode, timestamps, short IDs and filters |
| Failure guidance | Distinguishes research denial, output blocking and provider failure with safe next actions |
| Readability | Shared typography/spacing tokens, responsive layouts, keyboard focus and skip navigation |
| Packaging | Reproducible source archive with a file-hash manifest and local/private exclusions |

Request revision records feedback. It does not automatically edit the brief, regenerate it or create a linked child run.

## 6. What Nebius and PriviLAB each contribute

### Nebius and NVIDIA: live draft generation

The server calls Nebius Token Factory using:

~~~text
Endpoint: https://api.tokenfactory.nebius.com/v1
Model:    nvidia/Nemotron-3_5-Lightning
~~~

The key stays in private server configuration. The model receives the question and authorized, escaped evidence excerpts. It has no application tools to expand retrieval, change scope or approve research.

The adapter bounds generation to a total deadline of 45 seconds and a configured output budget capped at 900 tokens. It allows at most two transport attempts for bounded malformed-JSON regeneration. A timeout or incomplete response does not silently become a fixture result.

This is actual runtime inference through Nebius. The local web server is not deployed on a Nebius VM or AI Cloud endpoint. Do not describe it as such.

### PriviLAB: selected code in the control layer

PriviLAB is reused through attributed source adaptations, not a network API connection. No PriviLAB credentials, remote service or separate application process are needed.

The reused logic includes the permission parser/evaluator, authorization-filtered retrieval-query pattern, exact source/chunk citation checks, and bounded fixture/review/strict-parsing portions. MatterGate supplies its own domain schema, run orchestration, interface and independently implemented Nebius transport.

Upstream: [DataStrategyLab/privilab](https://github.com/DataStrategyLab/privilab), pinned to `21baa4ccdc468bd6a30681344eb8ec3df752790a`. Apache-2.0 notices are retained under [third_party/privilab](third_party/privilab/NOTICE). The [reuse manifest](docs/upstream/privilab-manifest.json) identifies copied portions, original hashes, local destinations and modifications.

Do not imply upstream endorsement, reuse its branding or describe the full upstream application as installed. Changes to covered files require updating local hashes and modification notes.

## 7. Why the main decisions were made

| Decision | Problem it addresses | Tradeoff |
|---|---|---|
| Permission before retrieval | Prevent unauthorized source text from entering model context | Small explicit policy matrix limits supported scenarios |
| FastAPI, Jinja and minimal JavaScript | Keep a complete workflow inspectable with one local service | Less frontend machinery; server polling drives progress |
| SQLite/FTS5 | Reproducible local corpus, constrained queries and clear transactions | One-process demonstration, not a distributed service |
| Selected PriviLAB adaptations | Reuse concrete permission and provenance controls | Attribution and modification hashes need maintenance |
| Independent Nebius adapter | Make required runtime inference explicit without inheriting another provider's application | Transport, timeout and response contracts need their own tests |
| Statement-owned citations | Avoid asking a model to duplicate exactly matching prose in a separate citation list | Structural linkage still does not prove that evidence supports a claim |
| Separate human review | Keep model recommendations from becoming application approval | A person must inspect substance and missing facts |
| Explicit fixture mode | Demonstrate the workflow without a paid/provider dependency | Only one exact seeded question is supported offline |
| Validated diagnostics | Explain failures without exposing provider bodies, prompts or keys | Some metadata is unavailable and must stay unknown |
| Local chained audit | Detect inconsistent event history and show ordered decisions | A privileged administrator could rewrite the database and recompute hashes |
| Consolidated UI tokens | Fix both tiny text and the oversized first correction | Requires browser, zoom and narrow-screen verification |

## 8. What we learned while building

The first model configuration hit the 900-token output limit and returned incomplete output. Switching to Lightning with thinking disabled produced complete responses, but the early result schema required identical claim text in two places. Small wording differences then failed exact citation coverage.

We changed the wire contract so each statement owns its evidence references. The application projects the same accepted text into the public brief and citation list. It does not invent links or loosen source-scope validation.

We also separated the review-state check from known prohibited-output detection. These measure different things and should not fail as duplicates.

The operator found the original text too small. An initial global enlargement became too large. The current interface uses a deliberate scale instead of repeated blanket overrides.

The fixture fallback also caused confusion: it looked like a way to continue a failed or denied request. It is now explicitly a **separate fixture demo**, shown only after a live provider failure.

These were product changes prompted by one operator's experience. They are not evidence of population-wide issue frequency.

## 9. Verification and current confidence

### Automated and isolated-browser evidence

The implemented 0.2.0 source passed **101 automated tests**, including mocked provider failures, citation boundaries, review conflicts, integrity checks, receipt access and package exclusions.

An isolated headless Edge walkthrough completed the fixture, evidence-navigation, human-review, receipt-download and denial flow. Thirty-two screen/viewport checks passed across eight routes at 1440, 1024, 768 and 390 CSS-pixel widths. Separate CSS-zoom reflow and focused keyboard checks passed. The extracted source build also passed 101 tests using the already installed dependency environment.

One existing Starlette/HTTPX deprecation warning remains. A fresh dependency installation, real mobile-device acceptance and current remote CI verification are not established by these checks.

### Operator-confirmed live acceptance

On October 24, the operator completed the updated live flow, run prefix **08126a78**:

| Observation | Recorded value |
|---|---|
| Model | `nvidia/Nemotron-3_5-Lightning` |
| HTTP / finish reason | `200` / `stop` |
| Input / output tokens | 1,678 / 302 |
| Provider latency | 1,515 ms |
| Retrieval / provider transport attempts | 1 / 1 |
| Selected evidence / structural checks | 5 excerpts / 10 of 10 passed |
| Human disposition | Research draft approved |
| Receipt | JSON download confirmed |

The operator also confirmed inline evidence navigation and return, history filters, the unsupported-custom-fixture explanation, and readable native 200% browser zoom on the request form with no overlap.

The unsupported fixture run, prefix **caf19e58**, correctly displayed `FIXTURE_SCENARIO_UNSUPPORTED`. The earlier live run `358410d3` and denial walkthrough are retained as earlier evidence, not counted as new live trials.

This is one successful live acceptance run for the updated release. Its 1.515-second provider latency is an observation, not an overall response-time benchmark or service guarantee. The downloaded receipt's exclusions are tested automatically; the operator confirmed downloading it, not a separate field-by-field privacy inspection.

## 10. How to operate it

Detailed installation and the venv alternative are in [setup](docs/setup.md). The closest tested environment is Python 3.14 with SQLite FTS5 and the pinned dependencies. Use one worker.

Private configuration:

| Setting | Purpose |
|---|---|
| `MATTERGATE_SESSION_SECRET` | Signs the demo session; keep it stable and private |
| `NEBIUS_API_KEY` | Enables live inference; blank for fixture-only use |
| `NEBIUS_BASE_URL` / `NEBIUS_MODEL` | Approved provider endpoint and configured NVIDIA model |
| `MATTERGATE_DATABASE` | Local SQLite path, normally under ignored `data/` |
| `MODEL_TIMEOUT_SECONDS` / `MODEL_MAX_OUTPUT_TOKENS` | Bounded generation settings |

Start manually from the repository root:

~~~sh
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

Open `http://127.0.0.1:8000`. Restart after Python/configuration/prompt changes and hard-refresh after interface updates. Do not run a second worker against this demonstration to obtain durable background processing.

To validate or package:

~~~sh
.venv/bin/python -m pytest -o addopts='' -q
.venv/bin/python scripts/package_release.py
~~~

The archive is generated at `dist/mattergate-test-build.zip`. It is a source test build, not a standalone executable. Documentation changes made after packaging require rebuilding it before distribution; its old manifest cannot describe new files.


## 11. Where to change things

| Location | Responsibility |
|---|---|
| `app/main.py` | Routes, signed demo session, CSRF/origin checks, history and export access |
| `app/domain.py` | Request/scope/draft contracts and state transitions |
| `app/integrations/privilab/` | Adapted permission and citation code |
| `app/services/policy.py` / `retrieval.py` | Scope resolution and authorized evidence selection |
| `app/providers/nebius.py` / `diagnostics.py` | Bounded inference and validated metadata |
| `app/providers/fixture.py` | Exact-scenario offline response and hash check |
| `app/services/evaluation.py` | Ten structural controls |
| `app/services/review.py` | Decision eligibility, rationale and atomic writes |
| `app/services/runs.py` | Orchestration, persistence, instrumentation and recovery |
| `app/services/presentation.py` | Guidance, exact inline mapping and safe receipt projection |
| `app/persistence/` | SQLite schema, transactions and audit chaining |
| `app/seed/` | Synthetic/public corpus, policy and fixture manifest |
| `app/templates/` / `static/` | Interface, behavior and design tokens |
| `tests/` / `scripts/package_release.py` | Regression checks and source packaging |

The API uses signed demo-session context. Mutations require CSRF/origin validation; posted actor IDs alone cannot submit a decision. This is still a freely selectable identity simulation, not proof of a real user's role.

## 12. What to preserve

- Denial must stop before retrieval or inference.
- Scope dimensions and expiry must be checked before protected work.
- Unknown or missing references must fail; do not generate guessed citations.
- A blocked result must not render as a reviewable brief.
- Live failures must remain visibly live failures.
- Alex-only review and immutable prior decisions must remain server-controlled.
- Credentials, prompts and source bodies must stay out of diagnostics/audit/export.
- Receipt counts on legacy records must remain unknown when not instrumented.
- Old audit records must not be rewritten to look newly measured.
- Required licenses, notices and PriviLAB modification hashes must remain accurate.

## 13. Current limitations and remaining work

The corpus has six sources and a deliberately narrow policy. The public legal reference is an attributed paraphrase; internal policies/contracts are synthetic. Citation checks verify identifier linkage, not legal accuracy or semantic entailment. Known attack-string checks cover the seeded scenario, not every prompt-injection technique.

The app has freely selectable demo roles, local storage and one-process background tasks. It is not a production document system, legal advice service or compliance certification. Restarting blocks interrupted active runs; there is no durable distributed queue.

Next handoff priorities:

1. Inspect CI for the exact source revision being distributed. Implementation milestone `a7cba1b` contains the Evidence & Review changes.
2. Use the current PRD, setup guide and verification notes when maintaining this release.
3. Rebuild the source archive for each distribution and check the distributable contents.
4. Provide an actual judge-accessible demo/test-build URL and suitable testing instructions.
5. Record the public demo video and finalize the submission narrative and specific Nebius/NVIDIA feedback.
6. If stronger reliability evidence is needed, run a capped, recorded sequence of live trials and keep all outcomes.
7. Validate usefulness with willing target-role participants before making impact or time-saving claims.

Public deployment requires a separate access, isolation, persistence and cost-control design. Publishing this source repository alone does not provide that design.

## 14. Reading order

1. [Current PRD](mattergate-prd.md): requirements and acceptance status.
2. [User guide](docs/user-guide.md): supported workflows and role semantics.
3. [Architecture](docs/architecture.md) and [API](docs/api.md): implementation details.
4. [Testing](docs/testing.md): precise evidence and remaining qualifications.
5. [Operations](docs/operations.md): reason codes and recovery.
6. [PriviLAB reuse](docs/privilab-reuse.md): scope, attribution and upstream differences.
7. [Release guide](docs/release-guide.md) and [hackathon overview](docs/hackathon-submission.md): packaging and presentation.
