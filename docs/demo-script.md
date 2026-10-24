# Demo script — target 2 minutes 45 seconds

Use the exact revision and model configuration you will submit. Keep the final
video under three minutes. The script below is a proposed recording plan;
no video was recorded while preparing the documentation.

## Before recording

- Start one local worker with synthetic data and live Nebius configuration.
- Verify the selected model is `nvidia/Nemotron-3_5-Lightning`.
- Confirm you can complete the allowed run and the denial scenario.
- Use a clean browser view without key pages, terminal credentials or unrelated tabs.
- Do not reset a live request into a fixture while presenting it as inference.
- If live inference is slow, use a clearly labeled time cut; keep the actual
  provider event/metadata visible. Do not fabricate a successful run.

## 0:00–0:20 — The problem

**Say:** “Sensitive research needs a permission boundary before it needs an answer.
MatterGate is a legal and privacy research demo that checks who is asking and
what evidence they may use before model context is assembled.”

**Show:** Overview, demo disclosure and the two scenarios.

## 0:20–0:55 — Scope before inference

**Say:** “Jordan asks about a fictional vendor's support-triage workflow. The
application resolves a permission scope and retrieves only the authorized chunks.”

**Show:** Seeded EU request, Live mode, Scope granted, selected source/chunk IDs.

## 0:55–1:25 — Nebius and NVIDIA drafting

**Say:** “NVIDIA Nemotron 3.5 Lightning runs through Nebius Token Factory to draft
this brief. The model does not grant access or approval.”

**Show:** Completed provider invocation/model metadata, the brief and one
claim-to-evidence link. Explain that the material is synthetic.

## 1:25–1:55 — Checks and a human decision

**Say:** “Ten deterministic checks validate scope, structure, citation linkage and
workflow controls. Passing means ready for review. Alex makes a separate decision.”

**Show:** Ten checks, switch to Alex, add a synthetic rationale and record a
decision. Clarify that accepting the draft does not authorize sharing data.
Show REVIEW_SUBMITTED and hash-chain verification.

## 1:55–2:25 — Denial proof

**Say:** “When Jordan asks for restricted merger research, the application stops
before retrieval or inference. The audit trail shows the boundary.”

**Show:** Scenario 02, Denied, zero authorized sources and no retrieval/model events.

## 2:25–2:45 — Reuse and limits

**Say:** “MatterGate adapts permission and citation controls from PriviLAB under
Apache-2.0. Our app owns the Nebius integration, workflow and interface. This is a
synthetic research demonstration, with human review—not a legal decision service.”

**Show:** Status/control layer or repository attribution; close on the brief/audit view.

## Recording and submission notes

Name Nebius Token Factory and NVIDIA Nemotron aloud and in the project description.
The current [official rules](https://nebiusglobalaihackathon.devpost.com/rules)
require a public YouTube link; verify their latest requirements before submission.
Keep model and run labels visible. Fixture fallback is useful for resilience but
must be explicitly identified as fixture output.

The [submission brief](hackathon-submission.md) contains the project narrative and
draft feedback. Final video, repository and judge-access links remain to be supplied.
