# Verification and acceptance evidence

Last documented October 24, 2026. Browser and operator results refer to the
implemented 0.2.0 release (implementation commit `a7cba1b`). Local automated
results and archive checks are recorded separately below.

## Executed results

| Check | Result | Qualification |
|---|---|---|
| Current automated suite | 101 passed | Fixture data, temporary databases and mocked HTTP transport; no paid inference |
| Browser end-to-end | Passed | Isolated headless Microsoft Edge: fixture request, inline reference and return focus, Alex switch, approval, receipt download, Jordan return and denial |
| Responsive checks | 32 passed | Eight routes at 1440, 1024, 768 and 390 CSS-pixel widths; no page-wide overflow; visible content text at least 12px |
| Text contrast sample | Passed | Rendered Overview text foreground/background checks against 4.5:1 normal / 3:1 large text; not a comprehensive accessibility audit |
| Zoom reflow | Four automated routes passed; native form zoom confirmed | Automated 200% CSS zoom on request/review/brief/receipt; operator confirmed native 200% request-form zoom with no overlap |
| Keyboard | Passed focused scenarios | Skip-to-content, citation focus and return-to-claim; not every assistive-technology combination |
| Existing persisted records | Passed automated reopen check | Approved decision, evidence and audit unchanged after reopening the database |
| Package exclusions | Passed | Archive omits private/local state, symlinks, logs and local planning package; reproducible bytes checked |
| Earlier extracted test build | 101 passed; 83 source/assets files hashed | Executed from the extracted archive using the already installed pinned environment; not a fresh dependency installation |
| Earlier live NVIDIA/Nebius flow | Operator confirmed success | Run prefix 358410d3 predates this UI/diagnostics upgrade; 10/10 controls, approval and REVIEW SUBMITTED |
| Current remote CI | Not inspected for this working tree | Publish a reviewed revision and inspect its actual workflow |
| Updated live acceptance | Operator confirmed run 08126a78 | HTTP 200 / stop; 1,678 input and 302 output tokens; 1,515 ms provider latency; one retrieval and one transport attempt; five excerpts; 10/10 checks; Research draft approved |
| New interface acceptance | Operator confirmed | Inline citation/return navigation, receipt JSON download, history filters and unsupported-custom-fixture guidance |
| Repeated live sample | Pending | One updated live acceptance run is not a repeated reliability sample |
| Public judge access / video | Pending | Local archive is not an uploaded test-build link |

The original baseline was 73 tests; the pre-upgrade working tree passed 81.
The expanded suite was rerun during public-repository preparation: **101 passed**.
The refreshed source archive passed ZIP integrity and all 92 manifest hash checks;
exclusion checks confirmed private plans, historical drafts, generation prompts,
credentials and runtime state are absent. Common credential-pattern scanning
found no matches in packaged text files. All 23 public Markdown files passed
local link/image-reference checks. These are focused checks, not a security audit.

One Starlette/HTTPX deprecation warning remains.
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
