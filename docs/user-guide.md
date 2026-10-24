# User guide

## Demo identities

| Identity | Intended role | Supported action |
|---|---|---|
| Jordan | Sales Operations | Vendor risk assessment; denied restricted M&A access |
| Maya | Privacy Counsel | Vendor risk assessment; M&A remains denied in this MVP |
| Alex | Human Reviewer | Read run evidence and record a review decision |

The identity picker is an explicit simulation. Anyone using this local demo can
select an identity. The server checks signed session identity rather than trusting
a posted actor ID alone; there is no real login, SSO or credential-based role proof.

Requesters see their own runs. Alex can inspect runs for review.

## Run allowed vendor research

From Overview choose **Run allowed assessment**, or open **New research** with:

- Requester: Jordan.
- Matter: Vendor onboarding / Vendor X.
- Jurisdiction: EU.
- Purpose: Vendor risk assessment.
- Question: the prefilled question about EU customer contact data and support triage.
- Mode: Live if configured, or Fixture for the exact seeded question.

The server records permission before retrieving text. An allowed run selects up
to five evidence chunks and produces a bounded brief. Live recommendations may
vary with the evidence and model output.

**Ready for review** means the defined structural checks passed. It is neither
human approval nor proof of legal accuracy.

## Inspect the brief

The brief contains scope, summary, conditions, caveats, questions and a draft
recommendation. Numbered links beside each material statement open and focus the relevant evidence excerpt. Use Return to the claim to resume reading. Sources show
classification, authority tier, source/chunk IDs, version and content hash.

Each live material statement carries chunk IDs in the provider response. The
application displays the same statement and checks that the IDs resolve inside
the selected evidence. This establishes linkage, not semantic entailment.

The injected-command test source is untrusted data. Detection and passing string
checks demonstrate only the bounded scenario. The application exposes no model
tools that can retrieve additional documents or grant permission.

## Human review

Open **Human review**, then **Continue as Alex** if needed. Inspect the draft and:

- **Approve draft**: optional note.
- **Request revision**: nonblank rationale required.
- **Reject**: nonblank rationale required.

Only `READY_FOR_REVIEW` runs accept a decision. A decision is recorded once and
cannot be overwritten. The audit trail gains `REVIEW_SUBMITTED`.

Approving a brief that recommends `DO_NOT_PROCEED` accepts that assessment.
It does not authorize data sharing. Requesting revision records a disposition;
there is no automatic edit/regeneration loop. A new research execution creates
a new run ID.

## Demonstrate denial

Return to Overview and choose **Scenario 02 — See the blocked request**.
This explicitly switches to Jordan and requests restricted M&A research.

Expected: `DENIED`, no authorized sources, no generated answer and no retrieval
or model-call events. The displayed explanation must not reveal restricted source
titles, IDs or content.

## Understand fixture fallback

**Start separate fixture demo** appears only after a live provider failure.
It creates a different, allowed seeded request in fixture mode. It does not change
the failed run, override a denial, or replace a live result in place.

Unsupported custom fixture requests block with `FIXTURE_SCENARIO_UNSUPPORTED`.
Change the question only in live mode; purpose/matter combinations remain subject
to the small policy matrix.

## Inspect the run receipt and audit

The Run receipt tab summarizes permission, selected evidence, structural controls, provider execution and the human disposition. New runs show measured retrieval/transport attempts; older records say Not recorded. The permission-checked receipt download excludes questions, excerpts, prompts, credentials and rationale. It still contains run and demo-identity metadata.

Expand an audit event to inspect safe metadata, timestamps and chained hashes. Source bodies, full
prompts, free-text rationale and credentials are excluded from event payloads.
The review rationale is stored separately with the review decision.

`Hash chain verified` indicates the local event chain is consistent. It does not
mean externally notarized or administrator-proof. See [threat model](threat-model.md).
