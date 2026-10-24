# Hackathon project overview

MatterGate was built for the **Nebius × NVIDIA Global AI Hackathon**.
It demonstrates permissioned legal/privacy research with actual runtime inference
through Nebius Token Factory.

![MatterGate — Permission before context](images/devpost/mattergate-thumbnail.png)

## The idea

Sensitive research requires a traceable chain: who may access the evidence,
what supports the draft and who reviewed it. MatterGate checks permission before
retrieval or inference, then keeps evidence, structural checks and human disposition
visible in one workflow.

The fictional example asks whether EU customer contact data can be shared with
Vendor X for support-ticket triage. A second example denies restricted M&A research
before retrieval or generation.

## What was built

- A complete request, permission, evidence, drafting, evaluation and review workflow.
- Inline evidence references and a separate human disposition.
- Safe provider diagnostics, measured attempts, history filters and downloadable receipts.
- A local audit ledger with SHA-256 chain verification.
- An explicitly labeled, hash-verified fixture for reproducible offline use.

## NVIDIA and Nebius

The live adapter calls `nvidia/Nemotron-3_5-Lightning` through
`https://api.tokenfactory.nebius.com/v1/chat/completions`.
Inference runs on Nebius; the web application runs locally. No Nebius VM or
dedicated compute deployment is claimed.

The operator-confirmed updated run completed with HTTP 200, 302 output tokens,
one provider transport attempt, 10/10 structural checks and human draft approval.
Its measured 1,515 ms provider latency describes one run, not a benchmark.
See [verification](testing.md) and [screenshots](images/devpost/README.md).

## Engineering lessons

Early generation exhausted the application's 900-token budget. Lightning with
thinking disabled completed within the budget. A second issue came from requiring
identical claim prose in two parts of the model response. Statement-owned citations
removed that duplication while preserving exact source-scope validation.

The interface also needed a deliberate typography scale, clear separation between
research permission and business authorization, and explicit fixture behavior.

## Original work and attribution

MatterGate supplies the scenario, domain contracts, Nebius transport, orchestration,
interface, receipts and documentation. Selected permission, retrieval, citation,
fixture and review logic adapts Apache-2.0 PriviLAB source at revision
`21baa4ccdc468bd6a30681344eb8ec3df752790a`.

Credit **Data Strategy Lab LLC** and upstream Creator & Lead Architect
**Andrew Tsintsiruk**. See [reuse details](privilab-reuse.md) and
[notices](../third_party/privilab/NOTICE). Development was AI-assisted with Codex;
the operator configured credentials and performed the live walkthrough and review.
The thumbnail is AI-generated artwork; product screenshots are real browser captures.

## Scope

This demonstration uses synthetic internal material and an attributed public
reference. It is not legal advice or a production authentication system.
Citation linkage does not prove legal accuracy, and local hash verification is
not externally anchored audit integrity. Draft approval accepts the assessment;
it never authorizes data sharing.

[Repository](https://github.com/NaveenGali11/MatterGate) ·
[Setup](setup.md) · [Demo walkthrough](demo-script.md) · [Limitations](threat-model.md)
