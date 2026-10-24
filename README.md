# MatterGate

<img src="docs/images/devpost/mattergate-thumbnail.png" alt="MatterGate — Permission before context" width="760">

**Permissioned legal research—policy before model context.**

MatterGate is a working research workflow for legal, privacy and compliance teams.
It establishes who is asking, why they are asking, and which evidence they may
use **before** retrieval or model inference. NVIDIA Nemotron on **Nebius Token
Factory** drafts a cited research brief; application code checks the output, and
a separate human reviewer records the decision.

> Demonstration only. Uses synthetic internal documents and an attributed public
> reference. It does not provide legal advice, make legal decisions, or establish
> compliance.

[Handover](HANDOVER.md) · [Current PRD](mattergate-prd.md) ·
[Setup](docs/setup.md) · [User guide](docs/user-guide.md) ·
[Architecture](docs/architecture.md) · [API](docs/api.md) ·
[Verification](docs/testing.md) · [Hackathon overview](docs/hackathon-submission.md)

![Live research brief with authorized evidence beside each claim](docs/images/devpost/01-live-evidence-review.jpg)

*Actual live NVIDIA/Nebius run with synthetic/public evidence. The thumbnail above
is promotional artwork; this workspace is a real product screenshot.
[View the gallery](docs/images/devpost/README.md). Structural checks do not establish legal accuracy.*

## What it does

- Resolves requester, matter, purpose and jurisdiction into an explicit access scope.
- Retrieves at most five authorized SQLite FTS5 chunks before building model context.
- Calls `nvidia/Nemotron-3_5-Lightning` through Nebius Token Factory in live mode.
- Produces a structured brief with claim-to-evidence links, caveats and open questions.
- Runs ten deterministic checks before making a draft available for review.
- Allows Alex, the seeded reviewer identity, to approve, reject or request revision.
- Preserves safe event metadata in an append-only SQLite audit ledger with hash-chain verification.
- Denies restricted requests before retrieval and provider invocation.
- Offers an explicitly labeled fixture mode for reproducible offline demonstrations.

This is a bounded application workflow. It does not browse the web, invoke
model-selected tools, upload files, or approve its own output.

## Verified demonstration

On October 24, 2026, the operator completed updated live run `08126a78`:
NVIDIA Nemotron on Nebius returned a complete draft, all **10 structural controls
passed**, and a separate reviewer approved the research assessment.

The receipt records **one provider transport attempt**, **302 output tokens** and
**1,515 ms provider latency**. These are observations from one run, not a benchmark.
Evidence navigation, receipt download, history filters and native 200% request-form
zoom were also confirmed.

![Live run receipt showing provider execution, checks and human disposition](docs/images/devpost/02-nebius-live-receipt.jpg)

The release passed **101 local automated tests** using fixtures and mocked
transports. Isolated browser QA completed the fixture/review/denial/download flow
and 32 route/viewport checks. Remote CI is separate from these local results.
See [verification evidence](docs/testing.md) and the [release guide](docs/release-guide.md).

## Start locally

Use Python 3.14 for the closest match to the verified development environment.
The project declares Python 3.12+, but that full version/platform range has not
been qualified. SQLite needs FTS5 support. Use one application worker.

From a clone or downloaded copy of this repository:

~~~sh
uv venv --python python3
uv pip install --python .venv/bin/python -r requirements.lock -e .
~~~

If `.env` does not already exist, copy `.env.example` to `.env`. For fixture mode,
leave `NEBIUS_API_KEY` blank. Generate a private session secret:

~~~sh
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Set `MATTERGATE_SESSION_SECRET` to that generated value in `.env`, then start:

~~~sh
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). The app creates its local database
and seeds demo records automatically. You can also run `.venv/bin/python -m app.seed`.
Keep the server terminal open; stop with Ctrl+C.

Full instructions, a standard-venv alternative and configuration bounds:
[docs/setup.md](docs/setup.md).

## Enable live Nebius inference

Create a key in [Nebius Token Factory](https://tokenfactory.nebius.com) and configure
these server-side values in `.env`:

~~~dotenv
NEBIUS_API_KEY=your_private_key
NEBIUS_BASE_URL=https://api.tokenfactory.nebius.com/v1
NEBIUS_MODEL=nvidia/Nemotron-3_5-Lightning
~~~

Never commit `.env` or place credentials in client-side code. Restart after changing
configuration. A configured key enables live attempts; only a completed provider
call establishes that inference worked.

The independently implemented HTTPX adapter calls `/chat/completions` with normal
TLS verification, a restricted HTTPS host allowlist, no redirects or environment
proxies, at most 900 output tokens and one total 45-second deadline. For the
supported Lightning/Super identifiers, it requests thinking off. At most one
regeneration attempt is made for malformed output within that same deadline.

The live model uses a **cited-statement wire schema**: each summary, condition
and caveat owns its claim text and chunk IDs. The app projects those unchanged
statements into the displayed brief and citation list. It does not invent links
or use fuzzy text matching to force an evaluation pass.

Model and endpoint references:
[Nebius's Nemotron notebook](https://github.com/nebius/token-factory-cookbook/blob/main/models/nemotron/run_nemotron.ipynb),
[Nebius API documentation](https://docs.tokenfactory.nebius.com/api-reference/introduction),
[NVIDIA's thinking-mode documentation](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/deployment-guide/deployment-guide-for-nemotron-3-on-trtllm.md).

The web server runs locally; inference runs on Nebius. No Nebius AI Cloud compute,
Serverless Jobs, DevPods, dedicated endpoint deployment or Tavily integration is
implemented or claimed.

## Try the two main scenarios

### Allowed research, followed by human review

1. Choose **Run allowed assessment**. Scenario cards use live mode when configured;
   otherwise, the supported fixture is selected.
2. Inspect the granted scope, selected evidence, brief and deterministic checks.
3. Open **Human review**, explicitly switch to Alex, and record a decision.
4. Inspect **REVIEW SUBMITTED** in the audit trail.

Approval accepts the research draft. It does not authorize the underlying data
sharing. The recommendation inside a draft can be **DO NOT PROCEED** while the
reviewer approves that assessment.

### Denied privileged request

Choose **Scenario 02 — See the blocked request**. It uses Jordan, restricted M&A
and transaction analysis. The result should be **Denied**, with no retrieval or
model-call events and no restricted source content.

**Start separate fixture demo** is offered only on a live provider failure. It
creates a new allowed fixture run; it cannot bypass a denial or evaluation block.
The existing run retains its original outcome.

The supported fixture is the exact seeded EU Vendor X question. Arbitrary custom
questions require live mode and may still be denied by the small policy matrix.

## Architecture

~~~mermaid
flowchart LR
    U[Research request] --> P{Permission}
    P -->|Deny| X[Safe denial]
    P -->|Allow + scope| R[Authorized FTS5 retrieval]
    R --> M[NVIDIA Nemotron via Nebius]
    M --> J[Strict parsing]
    J --> C{Deterministic controls}
    C -->|Fail| B[Blocked]
    C -->|Pass| H[Human review]
    H --> A[Approve / Reject / Request revision]
    X --> L[(Audit ledger)]
    B --> L
    A --> L
~~~

| Layer | Technology / responsibility |
|---|---|
| Web | FastAPI, Jinja templates, CSS and minimal JavaScript |
| Data | SQLite, FTS5, source/chunk versions and content hashes |
| Permissions | Adapted PriviLAB evaluator plus MatterGate scope rules |
| Drafting | Independent Nebius HTTPX adapter; separate hash-verified fixture |
| Evaluation | Pure deterministic checks, including exact source/chunk resolution |
| Review | Session identity, ready-state checks, rationale and conflict handling |
| Audit | Transactional, append-only safe events with per-run SHA-256 chaining |

The ten checks are `POLICY_ALLOW`, `EVIDENCE_NONEMPTY`, `OUTPUT_SCHEMA`,
`CITATION_PRESENT`, `CITATION_IN_SCOPE`, `CLAIM_COVERAGE`, `DISCLAIMER_EXACT`,
`NO_RESTRICTED_SOURCE`, `NO_UNTRUSTED_COMMAND_FOLLOWING` and `REVIEW_REQUIRED`.

[Architecture and data flow](docs/architecture.md) · [API contract](docs/api.md)

## Actual PriviLAB reuse

MatterGate adapts selected source from
[PriviLAB, commit 21baa4ccdc468bd6a30681344eb8ec3df752790a](https://github.com/DataStrategyLab/privilab/tree/21baa4ccdc468bd6a30681344eb8ec3df752790a):

- Strict permission policy parsing, evaluation and effective-allow gating.
- Authorization-first retrieval SQL and stable scoped ranking.
- Exact authorized-source and source/chunk citation checks.
- Selected fixture integrity and review eligibility/conflict logic.
- Boundary test cases.

These are executed local controls, not a PriviLAB API connection. The full upstream
app, live OpenAI adapter, bootstrap, Docker configuration, corpus and branding are
not included or enabled.

Credit: **Data Strategy Lab LLC**; upstream Creator & Lead Architect
**Andrew Tsintsiruk**. No affiliation or endorsement is implied. See the
[reuse assessment](docs/privilab-reuse.md),
[source/hash manifest](docs/upstream/privilab-manifest.json) and
[upstream notices](third_party/privilab/NOTICE).

## Scope and limits

- Demo identities are freely selectable. Signed sessions and actor checks do not
  constitute production authentication, SSO or enterprise access management.
- All internal documents and the transaction/vendor scenario are synthetic.
  The public legal reference is an attributed paraphrase; see [corpus notes](docs/corpus.md).
- Citation linkage and known attack-string checks do not prove factual/legal
  correctness or universal prompt-injection resistance.
- Audit chains are local and unanchored. A privileged administrator could rewrite
  the database and recompute them.
- Runs use one-process background tasks, not a durable distributed queue.
- Live answers can vary or fail. Fixture output is deterministic and labeled.
- A hosted, judge-accessible demo/test-build link has not yet been provided.
- There are no production readiness, privacy-retention, compliance or certification claims.

[Threat model](docs/threat-model.md) · [Operations and troubleshooting](docs/operations.md)

## Tests and contribution

~~~sh
.venv/bin/python -m pytest
~~~

The command runs local fixture and mock-transport tests, not paid inference calls.
The CI workflow is configured, but its latest result must be checked after publication.

[Testing and manual acceptance](docs/testing.md) · [Contributing](CONTRIBUTING.md) ·
[Security](SECURITY.md) · [Changelog](CHANGELOG.md)

## Publish and present

- [GitHub publication steps](docs/github-publishing.md)
- [Hackathon project overview](docs/hackathon-submission.md)
- [Demo script under three minutes](docs/demo-script.md)
- [Documentation index](docs/README.md)
- [Current PRD](mattergate-prd.md) and [roadmap](BUILD_PLAN.md)

Original MatterGate source is [MIT licensed](LICENSE). Adapted PriviLAB source
retains its Apache-2.0 license and notices under [third_party/privilab](third_party/privilab/LICENSE).
Other references and dependencies retain their own terms.
