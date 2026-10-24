# Verification and acceptance evidence

Last documented October 24, 2026. Results refer to the local 0.2.0 working tree
based on initial commit ff6c68b, with uncommitted Evidence & Review changes.

## Executed results

| Check | Result | Qualification |
|---|---|---|
| Current automated suite | 101 passed | Fixture data, temporary databases and mocked HTTP transport; no paid inference |
| Browser end-to-end | Passed | Isolated headless Microsoft Edge: fixture request, inline reference and return focus, Alex switch, approval, receipt download, Jordan return and denial |
| Responsive checks | 32 passed | Eight routes at 1440, 1024, 768 and 390 CSS-pixel widths; no page-wide overflow; visible content text at least 12px |
| Text contrast sample | Passed | Rendered Overview text foreground/background checks against 4.5:1 normal / 3:1 large text; not a comprehensive accessibility audit |
| Zoom reflow | Four routes passed | 200% CSS zoom on request, review, brief and receipt; native browser zoom remains untested |
| Keyboard | Passed focused scenarios | Skip-to-content, citation focus and return-to-claim; not every assistive-technology combination |
| Existing persisted records | Passed automated reopen check | Approved decision, evidence and audit unchanged after reopening the database |
| Package exclusions | Passed | Archive omits private/local state, symlinks, logs and local planning package; reproducible bytes checked |
| Extracted test build | 101 passed; 83 source/assets files hashed | Executed from the extracted archive using the already installed pinned environment; not a fresh dependency installation |
| Earlier live NVIDIA/Nebius flow | Operator confirmed success | Run prefix 358410d3 predates this UI/diagnostics upgrade; 10/10 controls, approval and REVIEW SUBMITTED |
| Current remote CI | Not inspected for this working tree | Publish a reviewed revision and inspect its actual workflow |
| Repeat paid live trials | Pending joint test | No live provider call made for this upgrade |
| Public judge access / video | Pending | Local archive is not an uploaded test-build link |

The original baseline was 73 tests; the pre-upgrade working tree passed 81.
The expanded suite now passes 101. One Starlette/HTTPX deprecation warning remains.
This warning was not suppressed or resolved through an unrelated dependency change.

Browser QA found and corrected a citation-focus problem and mobile table overflow
before the final pass. Temporary screenshots and raw reports are local ignored
artifacts. Selected clearly labeled fixture screenshots are in [images](images/README.md).

## Reproduce local checks

~~~sh
.venv/bin/python -m pytest -o addopts='' -q
~~~

The suite tests policy precedence and scope isolation, retrieval budgets, content
hashes, strict parsing, citation linkage, known attack-string controls, review
authorization/conflicts/transaction rollback, CSRF, read access, restart behavior,
bounded transport failures/repair, safe diagnostics, receipt access/export,
legacy counters, inline mappings, history filters and package exclusions.

No test makes a paid model call. CI uses the pinned Python/dependency setup in
.github/workflows/tests.yml. A local pass is not a remote CI result.

## Joint acceptance remaining

Use [the release walkthrough](release-guide.md) on the normal local server:

1. Complete a real live seeded request and inspect actual request ID, safe token
   data, latency and measured transport attempts.
2. Inspect every material claim against its source, including unsupported certainty
   or missing facts. Structural linkage does not establish source support.
3. Record Alex's intended disposition and inspect REVIEW SUBMITTED.
4. Check denial has zero measured attempts and no restricted evidence.
5. Try native 200% browser zoom and an actual mobile browser/device.
6. If doing a five-trial live rehearsal, keep every result and report the small
   sample honestly; do not replace failed runs with fixtures.
7. Have willing target-role users attempt the flow without coaching. No usability
   study, legal-quality review, time-saving benchmark or customer adoption is
   claimed by the automated walkthrough.

No claim of production load qualification, general prompt-injection immunity,
legal correctness or externally anchored audit integrity is made.
