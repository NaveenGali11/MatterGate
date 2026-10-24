# MVP trust boundaries

This is a local synthetic demo, not a production security assessment.

| Boundary | Implemented control | Limit |
|---|---|---|
| Browser to application | Signed session identity; actor-field matching; CSRF token and same-origin mutation checks; bounded JSON input | Anyone using the local demo can deliberately select a seeded identity. No SSO or real authentication. |
| Policy to retrieval | Adapted fail-closed evaluator; explicit source-ID scope; purpose/jurisdiction and metadata filters | The policy matrix is intentionally fixed and small; code/database administrators remain trusted. |
| Retrieval to provider | Valid scope/request binding; max five chunks and 8,000 text characters; verified source hashes | No claim of confidentiality or region guarantees from provider configuration alone. |
| Documents to model | Escaped fixed evidence envelopes; server prompt; no tools exposed | The known injection test is bounded; general prompt-injection immunity is not established. |
| Model to interface | Strict JSON and sizes; claim/citation linkage; exact disclosure; known restricted/injection checks; HTML escaping and CSP | Structural validation cannot prove legal or factual correctness. |
| Draft to review | Ready-state and evaluation checks; Alex session required; rationale rules; one immutable decision | Synthetic role simulation, not an enterprise approval system. |
| Workflow to audit | Transactional appends, safe field allowlist, immutable SQL triggers and per-run hash chains | No remote trust anchor, WORM storage or protection from a privileged database rewrite. |
| Application to Nebius | Allowed HTTPS hosts; normal TLS verification; no redirects/proxies; bounded response and total timeout | Live credentials/account/model availability were not tested during implementation. |

Run creation, state changes and review decisions do not commit if their required
audit append fails. The app hides generated drafts on denied/blocked runs and
refuses run reads when audit verification fails. Provider failures never silently
become fixture successes. Invalid generation may receive one regeneration attempt
within the same wall-clock budget; policy and deterministic evaluation failures do
not receive bypasses.

Questions/drafts in SQLite must remain synthetic. Avoid secrets in any question,
review rationale or model setting. Audit payloads exclude free-text questions,
source bodies, rationale, prompts and raw provider errors. Logs record only run
IDs and error class names; server access logs contain routes/statuses, not bodies.

One process owns background execution. Restart marks active runs blocked. There
is no distributed queue, production retention system, file upload, URL fetch tool,
privilege determination, autonomous execution or production deployment.
