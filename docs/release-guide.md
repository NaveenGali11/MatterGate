# Evidence & Review release — local test guide

Version 0.2.0, October 24, 2026. Implementation is local; no new commit, push,
deployment, GitHub release or hackathon submission is implied.

## Implemented

- One state-guidance mapping explains denial, output blocking, provider failure,
  review readiness and recorded dispositions.
- Material claims have adjacent evidence references. Opening a reference focuses
  the authorized excerpt; a return link restores the claim.
- Clear separation between research permission, model recommendation and
  approval of the research draft.
- Validated provider diagnostics: HTTP category/status, finish reason, request ID,
  token usage, latency and generation attempt when available.
- Transport-boundary attempt events include bounded JSON regeneration.
  New runs report measured retrieval/transport attempts; old runs say Not recorded.
- Run receipt with local integrity status and a permission-checked JSON download.
  Questions, excerpts, prompts, credentials and rationale are excluded.
- Run-history filters with timestamps, execution mode and short IDs.
- A consolidated responsive stylesheet, visible focus and skip navigation.
- Reproducible source test-build packaging that excludes private/local state.

The generation contract, authorization boundary, corpus and human-decision
state machine are preserved. No database schema migration is required; existing
audit records are not rewritten.

## Test together

Restart your normal local server to load the Python changes, then hard-refresh
the browser. The existing private `.env` remains unchanged.

1. Open Overview and launch the allowed vendor assessment in **Live** mode.
2. Open the brief. Select a numbered reference beside a condition, inspect the
   excerpt and select Return to the claim.
3. Open Human review, switch to Alex and record the intended decision.
   “Research draft approved” accepts the assessment, not a business action.
4. Open Run receipt. Check the actual model, completion, transport attempts,
   token metadata and review decision. Expand REVIEW SUBMITTED.
5. Download the safe receipt and inspect its allowlisted contents.
6. Switch back to Jordan. The current owned run stays open.
7. Run the restricted scenario. Verify denial, zero measured retrieval/provider
   attempts and no restricted evidence disclosure.
8. Use the history filters to distinguish the live reviewed run from older
   stopped and fixture runs.

A provider failure must remain a failure with safe diagnostics. The separate
fixture demo creates a new allowed offline run; it never changes the failed run.

The agent's browser checks used a separate temporary database and no Nebius key.
They did not add runs to the normal application database or make paid calls.

## Build a source test archive

~~~sh
.venv/bin/python scripts/package_release.py
~~~

The output is `dist/mattergate-test-build.zip` plus its printed SHA-256.
The archive includes a SHA-256 manifest and reproducible source/assets/setup
instructions. It excludes `.env`, local databases, caches, keys, logs, generated
artifacts and the local planning directory. Extract it, follow [setup](setup.md),
and start one worker.

This is a local artifact, not an uploaded release or public judge-access URL.
Live inference still needs server-side Nebius credentials; fixture mode does not.
A native browser-zoom pass, target-role user study, repeated paid live trials and
current remote CI verification remain separate acceptance tasks.

## Scope retained for later

Request revision records feedback; it does not automatically create/edit a child
run. Real authentication, arbitrary uploads, web retrieval and public hosted
multi-user operation remain outside this local demonstration.
