# Verification and acceptance evidence

Last updated October 28, 2026. Browser/operator results below were recorded on
October 24 for application version 0.2.0. The October 28 public-source cleanup
changes documentation, image selection, source packaging and CI checks; it does
not change the application runtime.

## Executed results

| Check | Result | Qualification |
|---|---|---|
| Local automated suite, October 28 | 101 passed | Fixture data, temporary databases and mocked HTTP transport; includes expanded packaging exclusions; no paid inference |
| Browser end-to-end | Passed | Isolated headless Microsoft Edge: fixture request, inline reference and return focus, Alex switch, approval, receipt download, Jordan return and denial |
| Responsive checks | 32 passed | Eight routes at 1440, 1024, 768 and 390 CSS-pixel widths; no page-wide overflow; visible content text at least 12px |
| Text contrast sample | Passed | Rendered Overview text foreground/background checks against 4.5:1 normal / 3:1 large text; not a comprehensive accessibility audit |
| Zoom reflow | Four automated routes passed; native form zoom confirmed | Automated 200% CSS zoom on request/review/brief/receipt; operator confirmed native 200% request-form zoom with no overlap |
| Keyboard | Passed focused scenarios | Skip-to-content, citation focus and return-to-claim; not every assistive-technology combination |
| Existing persisted records | Passed automated reopen check | Approved decision, evidence and audit unchanged after reopening the database |
| Package exclusions | Passed | Archive omits private/local state, symlinks, logs and local planning package; reproducible bytes checked |
| Earlier extracted test build | 101 passed; 83 source/assets files hashed | Executed from the extracted archive using the already installed pinned environment; not a fresh dependency installation |
| Earlier live NVIDIA/Nebius flow | Operator confirmed success | Run prefix 358410d3 predates this UI/diagnostics upgrade; 10/10 controls, approval and REVIEW SUBMITTED |
| Completed GitHub CI, inspected October 28 | Passed for `552a5fa`, `a7cba1b` and `ff6c68b` | [Latest inspected run](https://github.com/NaveenGali11/MatterGate/actions/runs/40139797857); this result predates the new release-check step |
| Updated live acceptance | Operator confirmed run 08126a78 | HTTP 200 / stop; 1,678 input and 302 output tokens; 1,515 ms provider latency; one retrieval and one transport attempt; five excerpts; 10/10 checks; Research draft approved |
| New interface acceptance | Operator confirmed | Inline citation/return navigation, receipt JSON download, history filters and unsupported-custom-fixture guidance |
| Repeated live sample | Pending | One updated live acceptance run is not a repeated reliability sample |
| Public judge access / video | Pending | Local archive is not an uploaded test-build link |

## Public-source cleanup checks - October 28

- Local automated suite: **101 passed**, one existing Starlette/HTTPX deprecation warning.
- `scripts/check_release.py`: **24 Markdown files**, local link/image targets,
  **seven unique PriviLAB adaptation hashes**, license notices and **87 archive files** checked.
- The source ZIP passed integrity and manifest hash checks. Packaging regressions
  cover private plans, historical drafts, generation prompts, hidden local files,
  database sidecars, key/certificate files, output and temporary PDF assets.
- Three reachable Git commits and 121 unique text blobs were scanned for common
  credential patterns and sensitive runtime paths. No matches were found. This
  is a focused check, not a guarantee or a comprehensive security audit.
- Six redundant earlier images were removed from the current public tree. The
  current gallery and thumbnail remain, with mode and provenance captions.
- Completed GitHub CI was verified through the authenticated GitHub CLI. The
  workflow now also runs release validation with read-only repository permissions.
  Check the result for the final cleanup commit separately.

The historical browser checks found and corrected citation focus and mobile table
overflow before their final pass. Those checks have not been rerun during this
source/documentation cleanup. Selected product screenshots are in [images](images/README.md).

## Reproduce local checks

~~~sh
.venv/bin/python -m pytest -o addopts='' -q
.venv/bin/python scripts/check_release.py
~~~

The suite tests policy precedence and scope isolation, retrieval budgets, content
hashes, strict parsing, citation linkage, known attack-string controls, review
authorization/conflicts/transaction rollback, CSRF, read access, restart behavior,
bounded transport failures/repair, safe diagnostics, receipt access/export,
legacy counters, inline mappings, history filters and package exclusions.

No test makes a paid model call. CI uses the pinned Python/dependency setup in
.github/workflows/tests.yml. A local pass is not a remote CI result.

## Operator-guided acceptance and remaining qualification

The operator completed the updated live seeded run, approved the research draft,
confirmed the receipt summary and shared provider diagnostics. They confirmed
the JSON download; field-by-field inspection of the downloaded contents was not
separately reported. Export exclusion/access checks are automated evidence.
The unsupported fixture run caf19e58 displayed its expected safe explanation.

Remaining qualification:

1. Review substantive source support and unsupported certainty with a suitably
   qualified participant. Structural linkage and operator navigation do not
   establish legal correctness.
2. If desired, repeat the updated denial scenario manually; automated/browser
   denial checks and an earlier operator denial are already recorded.
3. Test an actual mobile device and broader assistive-technology combinations.
4. For a five-trial live rehearsal, keep every outcome and report the small sample
   honestly; do not replace failed runs with fixtures.
5. Validate usefulness with target-role participants. No usability study, legal
   benchmark, time savings or customer adoption is claimed.
6. Verify the intended published revision and CI. Rebuild the source archive
   whenever distribution contents change.

No claim of production load qualification, general prompt-injection immunity,
legal correctness or externally anchored audit integrity is made.
