# Implementation status and roadmap

Version 0.2.0 · October 24, 2026. Requirements are defined in the
[current PRD](mattergate-prd.md); design decisions are explained in the
[handover](HANDOVER.md).

## Implemented

| Area | Delivered behavior |
|---|---|
| Permission | Actor, matter, purpose and jurisdiction resolve an expiring source scope before retrieval or inference |
| Evidence | Bounded SQLite FTS5 retrieval intersects authorized source IDs and metadata; selected content hashes are checked |
| Generation | NVIDIA Nemotron through Nebius Token Factory, bounded HTTP transport and strict cited-statement output |
| Offline demonstration | Exact seeded EU Vendor X scenario, with a hash-verified fixture and explicit mode label |
| Controls | Ten deterministic checks; a failed check withholds the reviewable draft |
| Human review | Server-validated demo reviewer, rationale rules, one immutable disposition and transactional audit |
| Evidence workspace | Inline references, source excerpts and return-to-claim navigation |
| Diagnostics | Validated provider metadata, measured attempts for new runs and safe failure guidance |
| Receipts | Permission-checked JSON export and locally verified audit chain |
| Usability | Responsive typography, visible keyboard focus, history filters and distinct live/fixture states |
| Source reuse | Attributed PriviLAB adaptations with pinned revision, source manifest and Apache-2.0 notices |
| Distribution | Pinned dependencies, CI workflow, setup guides and reproducible source packaging |

## Recorded verification

The release has 101 passing local tests, a fixture browser walkthrough and
32 route/viewport checks. The operator completed an updated live run with
10/10 controls, human draft approval, receipt download, evidence navigation,
history filters and native 200% request-form zoom. See [testing](docs/testing.md)
for the methods, dates and limitations. A local pass does not establish remote CI,
legal correctness or production readiness.

## Next product milestones

1. Evaluate evidence support and workflow usefulness with willing target-role users.
2. Run a capped series of live trials and retain all outcomes before making reliability claims.
3. Test real mobile devices and broader assistive-technology combinations.
4. Design authenticated roles and tenant/source administration before handling real documents.
5. Add durable jobs, retention controls, isolation and cost controls before shared deployment.
6. Consider linked revision runs; the current action records feedback without regeneration.

Public demo access and video presentation are separate distribution work.
The local source repository does not provide a hosted service.

## Boundaries to preserve

Permission must precede retrieval and inference. Unknown references fail closed.
Model output cannot expand scope, approve research or authorize business action.
Live failures stay visible and never silently become fixture results.
Historical audit metadata is not rewritten to fabricate measurements.

The project currently excludes uploads, arbitrary URL ingestion, live web research,
vector search, SSO, production policy administration and autonomous approval.
