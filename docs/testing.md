# Verification and acceptance evidence

Last documented: October 24, 2026. This file separates executed evidence from
tests that exist in source but have not been rerun after later edits.

## Recorded evidence

| Evidence | Result | Qualification |
|---|---|---|
| Initial local automated baseline | 73 passed; one Starlette/HTTPX deprecation warning | Executed before later model, cited-statement, evaluator and UI edits |
| Initial browser walkthrough | Fixture draft, human review and safe denial worked | Agent-observed desktop walkthrough before final typography changes |
| Live NVIDIA/Nebius walkthrough | Operator showed Ready for review, 10/10 checks and hash-chain verification | Current cited-statement contract; run prefix `358410d3` |
| Live human approval | Operator confirmed Approved and REVIEW SUBMITTED | Human confirmation in the guided walkthrough |
| Restricted-request scenario | Operator confirmed the expected denial result after following the scenario instructions | Latest confirmation, not a new automated test run |
| Latest automated suite / GitHub Actions | Not rerun / not observed | Must be executed and inspected before claiming current tests or CI pass |
| Hosted judge demo / video | Not provided yet | Publication/submission work remains |

The live screenshots preserve the brief, pending-review panel and audit view.
They precede the operator's subsequent approval confirmation. See
[images](images/README.md). They are demonstration evidence, not a benchmark dataset.

## Run the suite

~~~sh
.venv/bin/python -m pytest
~~~

Tests use temporary databases, fixtures and mocked HTTP transport; they do not make
paid live inference calls. Do not use a fresh result from an earlier revision as
evidence for a later revision.

The CI workflow in `.github/workflows/tests.yml` uses Python 3.14, installs the
pinned dependencies and runs pytest. There is no published CI result yet.

## Coverage present in source

- Explicit-block precedence, missing context, unresolved conditions, invalid policy shape.
- Supported actor/matter/purpose combinations and explicit scope expiry/dimension checks.
- Retrieval authorization, evidence budgets, FTS escaping and scoped ranking isolation.
- Exact source/chunk citation pairs, missing citations, unknown IDs and claim coverage.
- Strict JSON, duplicate keys, malformed shape, exact disclosure and output limits.
- Known injected-command/approval checks and independent application review-state validation.
- Cited-statement projection with no invented links or dropped uncited conditions.
- Actor spoofing, CSRF/origin checks, cross-requester reads and rate limiting.
- All review outcomes, rationale rules, repeat/concurrent decisions and atomic audit rollback.
- Audit immutability/tampering, source-text tampering and restart interruption handling.
- Nebius request shape, thinking-off option, HTTP failures, timeout cancellation and bounded repair.
- Fixture byte/hash integrity and rejection of unsupported requests.
- HTML escaping of untrusted model content.

Some of these were added after the 73-test baseline and remain unexecuted.
Coverage in source is not a claim that every case currently passes.

## Manual acceptance for a new revision

1. Use a fresh database path and start one local worker.
2. With no Nebius key, run the exact seeded fixture and inspect labels, evidence and checks.
3. Run restricted M&A as Jordan; inspect the absence of retrieval/provider events.
4. With a valid private key, run the seeded question in live mode.
5. Confirm provider/model/request metadata, ten checks and Ready for review.
6. Review as Alex; inspect the final state and REVIEW_SUBMITTED.
7. Verify a non-reviewer cannot submit a review and an already-decided run cannot be decided again.
8. Inspect an evaluation-blocked run: no generated brief is rendered.
9. Refresh after restarting; verify completed runs persist and interrupted active runs block.
10. Check keyboard operation and narrow-screen layout. A dedicated mobile-browser
    acceptance pass is still outstanding.

There is no claim of legal correctness, comprehensive attack resistance,
production load qualification, protected holdout testing or statistical reliability.
