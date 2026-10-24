# Hackathon submission brief

Prepared October 24, 2026. These are draft answers to adapt to the actual Devpost
fields; they are not a submitted form or a claim that all eligibility conditions
have been satisfied.

## Official requirements checked

[Official rules](https://nebiusglobalaihackathon.devpost.com/rules), checked
October 24, 2026:

- Deadline: Friday, October 30, 2026, **1:00 p.m. EDT / 10:00 a.m. PDT**.
- An app must use an NVIDIA model and either runtime Token Factory inference or
  Nebius compute. Runtime inference is sufficient; hosting on Nebius compute is
  not mandatory.
- Provide a public licensed repository, setup instructions, project description,
  a judge-accessible demo/hosted app/test-build link, and a public YouTube video
  shorter than three minutes.
- Select a track, provide tool feedback, identify third-party integrations and
  disclose significant work added to an existing project when applicable.
- Keep the project available for judging; personally confirm entrant/team eligibility,
  ownership and access obligations before submitting.

Recommended fit: **Best Apps and Agents Track**. This is a project-fit recommendation,
not an organizer eligibility decision.

The [organizer's submission guidance](https://nebiusglobalaihackathon.devpost.com/updates/46205-how-to-build-a-winning-project)
also emphasizes specific feedback and naming the required technology in the
description, Built With field and spoken video narration.

## Project name

MatterGate

## Short description

Policy before AI: legal research with NVIDIA Nemotron on Nebius, scoped evidence,
deterministic checks, human review and an audit trail.

## Inspiration / problem

Sensitive research workflows need more than a fluent answer. Teams must know
whether the requester can access the material, which sources support a claim,
whether automated controls passed, and who accepted the resulting draft.

MatterGate makes those boundaries visible. It begins with identity, matter,
purpose and jurisdiction, then limits the evidence sent to the model. The goal
is a useful research aid with accountable review, using synthetic scenarios
rather than real client documents.

## What it does

A user asks whether a fictional sales team can share EU customer contact data
with Vendor X for support-ticket triage. The application resolves permissions,
retrieves only authorized source chunks, and calls NVIDIA Nemotron 3.5 Lightning
through the Nebius Token Factory inference API.

The model returns a structured research draft with cited statements, conditions,
caveats and questions for counsel. Ten deterministic controls validate scope,
schema, citation linkage, disclosure and workflow separation. Passing drafts
reach Ready for review; Alex can approve, reject or request revision.

A second scenario asks for restricted merger material. That request stops before
retrieval or provider invocation. The interface exposes the permission outcome,
evidence, checks, review decision and safe event history. A synthetic source also
contains a malicious instruction to demonstrate the known untrusted-content
boundary. The model has no tool that can expand its access.

## How it was built

Python/FastAPI serves a Jinja interface with minimal JavaScript. SQLite stores
synthetic source metadata, chunks, runs, evidence selections, evaluations, review
decisions and audit events; FTS5 performs bounded local search.

Selected Apache-2.0 PriviLAB source was adapted for permission evaluation,
authorization-first retrieval, exact citation checks and bounded fixture/review
logic. MatterGate owns its scenario policy, extended scopes, cited-brief contract,
Nebius adapter, state machine, reviewer session checks, audit chain and interface.

The live provider sends only authorized excerpts inside fixed untrusted-content
envelopes. Each material statement owns its chunk IDs, so the app can display the
same statement with its evidence links. Evaluation is application code, not a
second model's opinion.

## Nebius and NVIDIA use

**Service:** Nebius Token Factory runtime inference API.

**Primary model:** `nvidia/Nemotron-3_5-Lightning`.

**Endpoint:** `https://api.tokenfactory.nebius.com/v1/chat/completions`.

**Role:** Generate the structured research draft from scoped evidence. The
application retains authority over permissions, retrieval, checks and review.

The configured request uses a bounded output budget and thinking off for the
recognized model identifier. Provider/model/request metadata are inspectable in
the app. A user-run live request reached all ten passing checks, then human
approval and REVIEW_SUBMITTED.

The web app currently runs locally. Nebius AI Cloud compute, Serverless Jobs,
DevPods, dedicated endpoint deployment and Tavily are not used or claimed.

## Challenges and changes

The initial Super call returned a length stop at the application's 900-token
budget. Lightning with thinking off produced a complete response, but the first
response contract required the model to duplicate identical claim text in two
places. That made citation coverage fragile.

We changed the provider contract so each statement carries its evidence IDs.
The application projects the same claim text into the brief and citation list;
it does not invent a citation or relax source-scope checks. We also separated the
review-state check from the known attack-text detector and improved safe diagnostics.

The final manual walkthrough demonstrated the full live research/review path.
Earlier blocked runs remained visible, showing the real failure history.

## What was accomplished

- Actual NVIDIA inference through Nebius Token Factory.
- Permission-before-context ordering with explicit evidence scope.
- A cited live draft passing ten deterministic controls.
- A separate human decision and safe audit event.
- A denied research scenario without retrieval or inference.
- Source-level PriviLAB reuse with revision/hash attribution and license notices.
- A reproducible, clearly labeled offline fixture path.

These are workflow observations, not legal-quality, compliance or production
security guarantees. The latest automated suite still needs to be rerun after
the later edits; the previous baseline was 73 passing tests.

## What was learned

The model output contract is part of reliability engineering. Statement-owned
citations are easier to validate than duplicated prose, while scoped identifiers
and fail-closed application state keep permission independent from generation.
A successful inference call does not by itself make an answer reviewable.

Live output remains variable. Human review is still required, and structural
citation checks do not establish that a legal proposition is true.

## What's next

Rerun and inspect the latest tests, complete narrow-screen QA and repeated live
rehearsals, provide judge access, and record the demo. Product work beyond the
hackathon would require real authentication, source administration, substantive
evidence evaluation, operational controls and separately designed deployment.

## Built With

Nebius Token Factory; NVIDIA Nemotron 3.5 Lightning; Python; FastAPI; Pydantic;
SQLite; FTS5; Jinja2; HTTPX; HTML; CSS; JavaScript; selected PriviLAB source adaptations.

Do not list SSO, a vector database, Tavily, Nebius compute deployment or other
services that were not actually integrated.

## Required tool feedback — draft for the entrant to confirm

### Nebius Token Factory

**Used for:** Live inference to draft a structured brief from permission-scoped
synthetic/public evidence.

**Worked well:** A server-side key and standard chat-completions HTTP interface
connected to the local app. Successful calls returned completion and request
metadata that the workflow could expose without credentials.

**Needs work / documentation feedback:** Model-specific guidance on thinking
controls and token budgets would have helped this bounded-output integration.
Our early request exhausted the app's 900-token cap. This observation is about
our integration settings, not proof of an infrastructure outage.

**Onboarding:** A key was configured locally and a live request completed during
the guided walkthrough. No measured onboarding-time benchmark was collected.

**Would use again:** Proposed answer for your confirmation: yes, for hosted
inference with application-owned scope and review controls.

### NVIDIA Nemotron

**Used for:** The final drafting model was Nemotron 3.5 Lightning; Super was tried
earlier during debugging.

**Worked well:** Lightning produced the structured cited-statement response needed
for the demonstrated run after thinking was disabled and the contract was clarified.

**Needs work / integration lesson:** The model and prompt must fit the response
budget. Exact duplicated prose was brittle; per-statement evidence objects gave
the application a clearer validation boundary. We did not measure comparative
accuracy, legal correctness, latency distributions or model benchmark scores.

**Would use again:** Proposed answer: yes for bounded drafting with deterministic
validation and human review; confirm this reflects your own experience.

### Nebius AI Cloud compute

Not used directly in this implementation. The project uses Token Factory runtime
inference. There is no hands-on compute-deployment feedback to invent.

## Original work and third-party disclosure

MatterGate's application, vendor/M&A scenario, UI, Nebius transport, cited-brief
workflow and documentation were built during the October 24, 2026 development
session. Selected controls/tests were adapted from existing PriviLAB source at
commit `21baa4ccdc468bd6a30681344eb8ec3df752790a`.

Credit Data Strategy Lab LLC and upstream Creator & Lead Architect Andrew
Tsintsiruk. Preserve the Apache-2.0 attribution and identify our modifications.
Do not describe the upstream controls as wholly original MatterGate inventions.

Development was AI-assisted with Codex. The operator configured private credentials,
ran the successful live walkthrough, reviewed the interface, approved the synthetic
brief and confirmed the denial scenario. Confirm final authorship/team fields
and any required disclosure in the actual form.

## Assets and information still to supply

| Item | Current status |
|---|---|
| Public repository URL | Add after publishing; do not use a placeholder in the final form |
| Judge-accessible demo or test-build URL | Decide and provide; localhost is not accessible to judges |
| Public YouTube demo URL | Record/upload a video under three minutes |
| Team/entrant names and roles | Confirm manually |
| Latest test/CI result | Rerun and record actual outcome |
| Final tool-feedback answers | Review the draft above in your own voice |
| Publication commit/tag | Record after publishing; none is invented here |
| Mobile/repeat-run evidence | Still outstanding |

Use the [GitHub guide](github-publishing.md) and
[demo script](demo-script.md) next. Preparing these documents does not register,
submit, accept terms, publish a repository or deploy a service.
