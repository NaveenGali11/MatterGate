# Documentation

Start with the [product and engineering handover](../HANDOVER.md), then the
[current PRD](../mattergate-prd.md) or [project README](../README.md).

For a quick hands-on walkthrough, use the [teammate visual testing guide](team-testing-guide.md).

| Document | Contents |
|---|---|
| [Setup](setup.md) | Environment, installation, configuration and local startup |
| [User guide](user-guide.md) | Identities, scenarios, evidence, review and audit |
| [Teammate testing](team-testing-guide.md) | Screenshot-led walkthrough, expected outcomes, guardrails and bug-report template |
| [Architecture](architecture.md) | Trust boundaries, data flow, states and persistence |
| [API](api.md) | Sessions, CSRF, run operations, review, status and draft formats |
| [Testing](testing.md) | Recorded evidence, automated coverage and manual acceptance |
| [Release test guide](release-guide.md) | Current changes, test-together steps and source archive packaging |
| [Operations](operations.md) | Failures, restarts, fixture behavior and debugging |
| [AWS hosting](hosting.md) | Live URL, visitor isolation, inference limits, deployment and backup runbook |
| [PriviLAB reuse](privilab-reuse.md) | Pinned components, modifications, attribution and differences |
| [Source manifest](upstream/privilab-manifest.json) | Upstream revision, copied symbols and source/local hashes |
| [Corpus](corpus.md) | Synthetic material, public reference and source hashes |
| [Threat model](threat-model.md) | Implemented controls and important limits |
| [GitHub publishing](github-publishing.md) | Publication steps, private-file exclusions and final checks |
| [Hackathon overview](hackathon-submission.md) | Project story, NVIDIA/Nebius runtime use, lessons and attribution |
| [Demo script](demo-script.md) | A timed walkthrough shorter than three minutes |

The [PRD revision 2.0](../mattergate-prd.md) records current requirements and
implementation/acceptance status.
The [build plan](../BUILD_PLAN.md) records implementation status and remaining work.
When an original example differs from the implementation, this documentation and
the code describe the actual behavior. Important differences include asynchronous
HTTP 202 run creation, statement-owned citations and explicit fixture fallback.

Evidence is labeled by source: automated baseline, operator-observed live run,
or implementation inspection. An unexecuted test is never presented as passing.

## Product walkthrough

![Current live research and evidence workspace](images/devpost/01-live-evidence-review.jpg)

The [illustrated gallery](images/devpost/README.md) shows live evidence review,
provider receipts, human review and the permission boundary. These are real
synthetic/public demonstration views. [Image provenance](images/README.md).
