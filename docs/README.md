# Documentation

Start with the [project README](../README.md).

| Document | Contents |
|---|---|
| [Setup](setup.md) | Environment, installation, configuration and local startup |
| [User guide](user-guide.md) | Identities, scenarios, evidence, review and audit |
| [Architecture](architecture.md) | Trust boundaries, data flow, states and persistence |
| [API](api.md) | Sessions, CSRF, run operations, review, status and draft formats |
| [Testing](testing.md) | Recorded evidence, automated coverage and manual acceptance |
| [Release test guide](release-guide.md) | Current changes, test-together steps and source archive packaging |
| [Operations](operations.md) | Failures, restarts, fixture behavior and debugging |
| [PriviLAB reuse](privilab-reuse.md) | Pinned components, modifications, attribution and differences |
| [Source manifest](upstream/privilab-manifest.json) | Upstream revision, copied symbols and source/local hashes |
| [Corpus](corpus.md) | Synthetic material, public reference and source hashes |
| [Threat model](threat-model.md) | Implemented controls and important limits |
| [GitHub publishing](github-publishing.md) | Publication steps, private-file exclusions and final checks |
| [Hackathon submission](hackathon-submission.md) | Project narrative, technology use, feedback and missing links |
| [Demo script](demo-script.md) | A timed walkthrough shorter than three minutes |

The [PRD](../mattergate-prd.md) records the original requirements.
The [build plan](../BUILD_PLAN.md) records implementation status and remaining work.
When an original example differs from the implementation, this documentation and
the code describe the actual behavior. Important differences include asynchronous
HTTP 202 run creation, statement-owned citations and explicit fixture fallback.

Evidence is labeled by source: automated baseline, operator-observed live run,
or implementation inspection. An unexecuted test is never presented as passing.

The supplied current screenshots are in [images](images/README.md).
