# PriviLAB source reuse assessment

Inspected October 24, 2026. Repository: [DataStrategyLab/privilab](https://github.com/DataStrategyLab/privilab). Inspected commit: [`21baa4ccdc468bd6a30681344eb8ec3df752790a`](https://github.com/DataStrategyLab/privilab/commit/21baa4ccdc468bd6a30681344eb8ec3df752790a), committed October 23, 2026. This is a source assessment, not an execution, security certification, or report of passing upstream tests.

**Implementation follow-up:** The selected adaptations are implemented in MatterGate and execute in both provider modes. The initial local fixture/mock baseline passed; later tests still need rerunning. The operator subsequently demonstrated live Lightning inference with statement-owned citations and ten passing controls, then confirmed human approval and the denial scenario. See the [source manifest](upstream/privilab-manifest.json) for copied portions, original/local hashes and changes, and [testing](testing.md) for evidence qualifications. The assessment below preserves the pre-implementation rationale. Upstream's application was not installed or executed.

## Recommendation

PriviLAB is useful for MatterGate. Reuse selected code through small, attributed source adaptations, with tests ported to MatterGate's contracts. The reusable core consists of deterministic permission evaluation, authorization-filtered search, exact citation resolution, and some review/fixture validation logic.

Do not adopt the full app as a package, service, submodule, or fork. The adaptation approach gives MatterGate actual upstream-derived runtime logic while keeping the Nebius integration and PRD-specific behavior explicit. No application code was copied or executed during this assessment; the build plan now requires that integration and verification during implementation.

## What was inspected

The repository tree and current commit, dependency manifest, license/notice guide, release-status document, architecture, and selected implementation/test files were read through the GitHub connector. The source excerpts covered policy parsing/evaluation, scope construction, retrieval SQL and provider boundary, citation evaluators, review eligibility and writes, fixture manifest/hash validation, run orchestration, strict result parsing, and the default live-client restriction. This was targeted inspection, not an exhaustive audit of every repository file.

## Concrete reuse map

All source links below are pinned to the inspected commit.

| Upstream code | Useful implementation | Intended destination and changes |
|---|---|---|
| [`application/permissions.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/application/permissions.py) | `parse_permission_policy`, `evaluate_permission`, `permits_protected_progression`: strict field validation, immutable rules, explicit-block precedence, missing-context handling, unresolved-condition stop. | `app/integrations/privilab/permissions.py`, invoked by `services/policy.py`. Adapt selectors and types to MatterGate; add purpose/jurisdiction and reason-code projection. Preserve block precedence and effective-allow semantics. |
| [`domain/permissions.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/domain/permissions.py), [`application/retrieval.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/application/retrieval.py), [`domain/retrieval.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/domain/retrieval.py) | Effective allow is required before `access_scope_for` can mint an immutable capability; typed source/chunk IDs and source ownership validation. | Adapt the small validation/gating portions into our policy/domain boundary. Keep MatterGate's public `AccessScope` fields, source allowlist, version, actions, jurisdiction, and expiry. An internal constructor sentinel is an application convention, not authentication or protection from hostile Python code. |
| [`adapters/retrieval/sqlite_fts.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/adapters/retrieval/sqlite_fts.py) | `_RETRIEVE_SQL` builds authorized sources/chunks before returning matched text, binds values, and uses stable ordering. Its score uses matched-text density rather than global BM25 statistics. | Adapt SQL into our retrieval repository with explicit source-ID intersection, eligible purposes/jurisdictions/classifications, and fixed budgets. Retain ranking isolation: unrelated restricted documents must not alter authorized result ordering. Do not copy the complete schema/integrity implementation simply to reuse this query. |
| [`evals/evaluators.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/evals/evaluators.py) | `ProvenanceIndex`, `provenance_index`, `authorized_source`, `citation_resolution` verify membership in trusted source IDs and exact `(source_id, chunk_id)` pairs. | Adapt into `app/integrations/privilab/citations.py`, invoked by `services/evaluation.py`. Project MatterGate evidence and citations into trusted ID sets; derive source IDs from authorized chunk records rather than model assertions. Do not import the entire upstream provenance/evaluation model graph. |
| [`domain/research.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/domain/research.py) | Strict JSON parsing rejects duplicate fields, unexpected fields, wrong types, and malformed citation references. | Adapt duplicate-key rejection and relevant validation helpers into the MatterGate parser; retain our richer brief schema and size limits. |
| [`application/run_review.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/application/run_review.py), [`adapters/storage/sqlite_provenance.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/adapters/storage/sqlite_provenance.py) | Review eligibility depends on stored evaluation; contradictory evidence removes review actions; duplicate human review becomes a conflict. | Adapt the bounded eligibility/conflict portions into our review service/repository where useful. Implement Alex's session authorization, rationale, ready-state restriction, and atomic audit append ourselves. Leave the large storage module out. |
| [`adapters/models/governed_fixture.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/adapters/models/governed_fixture.py) | Fixture manifest identity, version, hash and path validation prevent mislabeled or modified fixture bytes from being accepted. | Adapt byte/hash verification and bounded manifest parsing into our fixture adapter. Use an original vendor-assessment payload and MatterGate-owned manifest, not the upstream task answers or package-resource layout. |

These are source adaptations, not claims that upstream components fit unchanged. Keep permission and citation modules small enough to review without inheriting unrelated application imports.

## Compatibility gaps that matter

1. **Context and scope:** Upstream policy selectors are user, role, client, matter, and workflow. They do not directly cover MatterGate's jurisdiction and purpose fields. Upstream `AccessScope` does not include the PRD's explicit allowed source IDs, expiry, policy version, or run binding. Extend the adapted contracts explicitly; do not silently drop these dimensions or encode them into a concatenated workflow string.

2. **Permission vocabulary:** Upstream has `ALLOW`, `BLOCK`, `UNKNOWN`, and `CONDITIONAL`. MatterGate must project these into safe public decisions and reason codes. Only effective allow proceeds. Client input must never mark conditions satisfied.

3. **Draft shape and generation boundary:** Upstream `ResearchResult` contains `answer_text` and source/chunk citations. It lacks our recommendation, conditions, caveats, open questions, and exact disclosure. Its provider port accepts an already-composed request without an `AccessScope` parameter. MatterGate keeps its own schema and adds the PRD-required scope checks directly at the provider boundary.

4. **Evaluation coverage:** Upstream implements four structural evaluators: permission boundary, authorized source, citation resolution, and provenance completeness. They do not supply all eight MatterGate checks or prove that prose is entailed by cited text. A legitimate denied run can pass upstream's permission-boundary criterion while its output gate remains blocked. MatterGate must distinguish correct denial behavior from eligibility to display/approve an answer.

5. **Review semantics:** Upstream `HumanReview` uses a fixed `synthetic-local-reviewer`, has no rationale field, and permits reject/revision on generated drafts even when the automated gate blocks approval. MatterGate requires server session identity, Alex-only review, reject/revision rationale, and `READY_FOR_REVIEW` for every action. Reuse validation logic with these deliberate changes.

6. **Storage and progress:** Upstream finalized metadata records do not retain full answer/task/query/source bodies for replay, and the storage model is not the PRD's per-stage event hash chain. MatterGate needs persistent synthetic draft/evidence views, live progress events, audit chaining, and transaction rules. Build those repositories for our own contract; adopt minimum safe audit payloads as a design principle.

7. **Retrieval:** Upstream entitlements are exact matches with no wildcard semantics; defaults allow up to ten retrieved chunks. Normalize all-matter/public source permissions explicitly, enforce our smaller limits, and sanitize plain-language questions into bounded FTS expressions. Do not expose arbitrary MATCH syntax as a permission mechanism.

## Why not use the upstream package or live adapter?

The inspected [`pyproject.toml`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/pyproject.toml) requires Python `>=3.13,<3.14`, pins the build/tool environment, and includes the OpenAI SDK with the web framework dependencies. Installing the entire package would bring a runtime/dependency contract that our small source adaptations do not need.

The [`OpenAI adapter`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/src/privilab/adapters/models/openai.py) targets the OpenAI Responses API and fixes its destination. `_require_live_qualification()` unconditionally raises before default client construction and credential access. It is not a Nebius adapter that can be enabled by changing a base URL.

The upstream [`release status`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/docs/release-status.md) documents fresh native-networked setup and Docker qualification holds and a disabled default live SDK. Those are material limitations of adopting that execution path. We did not execute it. Source adaptation does not establish that a new MatterGate transport is safe or functional: validate its dependencies, normal TLS certificate verification, endpoint, timeout/error handling, and actual Nebius execution independently. Do not remove the upstream restriction or carry over its approval claims.

## Tests to port and extend

- [`test_permission_fail_closed.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/tests/integration/test_permission_fail_closed.py): missing context, explicit block, unresolved conditions, effective allow.
- [`test_retrieval_authorization_boundary.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/tests/security/test_retrieval_authorization_boundary.py): isolation for every scope dimension, invalid scope, malformed FTS, and untrusted text. Add purpose, jurisdiction, source allowlist, expiry, and ranking isolation.
- [`test_evaluations.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/tests/unit/test_evaluations.py): wrong sources/chunks, empty citations, cross-run provenance, evaluator exceptions, and denial/output-gate separation. Adapt assertions to MatterGate's check codes.
- [`test_run_review.py`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/tests/unit/test_run_review.py): contradictory evaluation and ineligible actions. Add identity spoofing, rationale validation, concurrency conflicts, and failed audit transaction behavior.

Port the cases and any useful helper source with attribution. Upstream tests depend on upstream preview/contracts and cannot be copied unchanged and treated as proof of MatterGate's behavior. No upstream or adapted runtime tests were run for this planning task.

## License, attribution, and reproducibility

The inspected [`LICENSE`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/LICENSE), [`NOTICE`](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/NOTICE), and [license guide](https://github.com/DataStrategyLab/privilab/blob/21baa4ccdc468bd6a30681344eb8ec3df752790a/licenses/README.md) identify project-authored code and original synthetic material as Apache-2.0, subject to separately identified third-party terms. For the planned adaptations:

- Preserve the license and relevant copyright/NOTICE text; mark modified files prominently.
- Create `docs/upstream/privilab-manifest.json` with repository, commit, path, SHA-256 of source bytes, symbols/excerpts reused, local destination, and modification summary. Confirm fetched files match the pinned revision at extraction time.
- Add `third_party/privilab/LICENSE` and `NOTICE` when source is incorporated. Record any other terms applicable to the exact copied material; do not treat the upstream dependency inventory as licenses for bytes we did not copy.
- Credit Data Strategy Lab and upstream Creator & Lead Architect Andrew Tsintsiruk in README acknowledgments, without implying affiliation or endorsement.
- Exclude logos, brand assets, and domain task/corpus content. Build original MatterGate synthetic vendor/M&A fixtures and separately attributed public references.
- Describe the implementation after integration as: “MatterGate adapts selected permission and citation controls from PriviLAB (Apache-2.0); Nebius inference, application workflow, and interface are implemented for MatterGate.” Until it exists, describe this as planned reuse.

## Acceptance criteria for actual integration

1. Permission resolution calls the adapted upstream-derived evaluator before any retrieval/model invocation.
2. Retrieval SQL preserves authorization filtering and bounded evidence selection; both live and fixture runs use it.
3. The deterministic evaluation gate executes adapted exact source/chunk checks and the remaining MatterGate rules.
4. Ported tests preserve the relevant upstream invariants and verify our intentionally different contracts.
5. A source manifest, license/notice files, modification notices, and README acknowledgment are present.
6. Nebius integration works independently without importing or enabling the held upstream live execution path.

This makes PriviLAB a concrete source contribution to the planned application, with its scope and limitations visible to a reviewer.
