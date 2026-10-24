# Changelog

## 0.1.0 — Hackathon MVP — 2026-10-24

### Implemented

- FastAPI/Jinja local interface with scenario picker, request form, progress,
  brief, human review, audit and system status.
- Seeded identities, policies and six synthetic/public-reference sources.
- Selected attributed PriviLAB permission, retrieval, citation, fixture and review adaptations.
- Explicit scopes, source eligibility, FTS5 ranking, evidence budgets and content hashes.
- Independent Nebius NVIDIA inference transport and distinct fixture provider.
- Strict JSON parsing and statement-owned citations projected into the brief.
- Ten deterministic controls with safe failure reasons.
- Reviewer identity/state/rationale checks and immutable decisions.
- Transactional audit events, local hash-chain verification and restart handling.
- CSRF, same-origin checks, bounded inputs, HTML escaping and CSP.
- Pinned dependency list, local test suite and GitHub Actions workflow.
- Setup/API/user/operations documentation, source attribution and submission draft.

### Observed verification

- Initial automated baseline: 73 passed before subsequent changes.
- Operator completed a live Lightning request with all ten controls passing,
  human approval and REVIEW_SUBMITTED.
- Operator confirmed the restricted-request denial flow.

### Remaining

- Rerun the automated suite against the latest edits and inspect remote CI.
- Dedicated mobile QA and repeat live rehearsal.
- Publish the repository, provide judge-accessible demo/test-build access,
  record the public video and complete the submission fields.

A version heading records this source milestone; no Git tag, GitHub release,
hosted deployment or submission is implied.
