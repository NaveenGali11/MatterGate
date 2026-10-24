# Contributing

MatterGate is a local, synthetic hackathon research workflow. Read the
[README](README.md), [architecture](docs/architecture.md) and
[threat model](docs/threat-model.md) before changing control boundaries.

## Development

Follow [setup](docs/setup.md), then run:

~~~sh
.venv/bin/python -m pytest
~~~

Use temporary databases and synthetic fixtures. A normal test run must not require
Nebius credentials or make paid provider calls. Keep real client data, personal
information and credentials out of code, test inputs, issues and screenshots.

## Changes that need particular care

- Authorization must complete before retrieval or provider invocation.
- Retrieved and cited IDs must remain inside the persisted permission scope.
- Live statements must own their evidence links; do not fabricate or fuzzy-match citations.
- Invalid or blocked drafts must not appear as reviewable briefs.
- Human review must remain separate from model output and use server-validated identity/state.
- State/decision writes and their required audit events must remain atomic.
- Fixture mode must be explicit and limited to the supported seeded scenario.
- No model-selected retrieval tools, arbitrary URL fetches or uploads are in scope.

For a change, explain the user-visible result, relevant invariants, tests actually
run, and any unverified behavior. Do not report historical tests as a current pass.

## Upstream adaptations

Selected PriviLAB-derived files carry Apache-2.0 attribution. Preserve those
notices and `third_party/privilab/LICENSE` and `NOTICE`. When changing a listed
adaptation, update the local file hash and modification summary in
`docs/upstream/privilab-manifest.json`. Pin any new upstream extraction to a
specific revision and record its source hash and copied symbols.

Do not import upstream branding, confidential materials or the held upstream
live/bootstrap execution path. Other third-party material retains its own terms.

## Publication

Original MatterGate source uses the root MIT license; this does not relicense
the adapted PriviLAB portions. See [publication steps](docs/github-publishing.md)
and [security guidance](SECURITY.md).
