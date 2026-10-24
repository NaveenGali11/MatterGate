# Operations and troubleshooting

Run on localhost with one worker. Configuration is loaded at process startup.
Restart after editing `.env` or Python/prompt files. CSS changes normally require
only a browser refresh; Cmd+Shift+R forces a refresh on the demonstrated Mac setup.

## Status interpretation

| State / code | Meaning | Action |
|---|---|---|
| `READY_FOR_REVIEW` | Defined checks passed | Inspect the brief; record a human decision |
| `DENIED` | Policy did not permit the request | Check the intended seeded scenario; fixture mode is not a bypass |
| `EVALUATION_FAILED` | One or more output controls failed | Read the individual check reasons; create a new run after fixing the cause |
| `PROVIDER_NOT_CONFIGURED` / live form disabled | Missing key or invalid endpoint/model settings | Inspect configuration locally; never share the key |
| `PROVIDER_AUTH_ERROR` | Provider returned 401/403 | Check the private server key and account access |
| `PROVIDER_RATE_LIMITED` | Provider returned 429 | Wait, then explicitly start a new run |
| `PROVIDER_HTTP_ERROR` | Other non-200 provider response | Check provider availability, model and account access |
| `PROVIDER_TIMEOUT` | Total generation deadline expired | Check provider availability and retry explicitly |
| `PROVIDER_INCOMPLETE_OUTPUT` | Provider finish reason was not stop | Inspect safe finish/token metadata; do not treat partial JSON as a brief |
| `PROVIDER_INVALID_RESPONSE` | Transport/response shape could not be accepted | Check endpoint/provider compatibility |
| `FIXTURE_SCENARIO_UNSUPPORTED` | Fixture request differs from the seeded scenario | Restore the seeded EU question or use live mode |
| `FIXTURE_EVIDENCE_MISMATCH` / `FIXTURE_INTEGRITY_FAILED` | Fixture context or registered bytes differ | Inspect source/fixture versions; do not bypass the hash check |
| `PROCESS_INTERRUPTED` | An active run existed at process restart | Start a new run; the original remains blocked |
| `CONTROL_INTEGRITY_FAILED` | Run read could not validate audit/evidence | Preserve the database for investigation; do not present the result as approved |
| `REVIEW_NOT_AVAILABLE` | Wrong state or already reviewed | Refresh and inspect the existing decision |
| `CSRF_CHECK_FAILED` | Stale token or origin mismatch | Refresh, confirm identity, retry the intended action |
| `RUN_LIMIT_REACHED` | Six requests per session per minute reached | Wait before starting another run |

## What fixed the observed live failures

The initial Super request stopped at 900 output tokens. Lightning with thinking
disabled completed, but output initially failed citation coverage and attack-text
checks. The prompt was tightened, the duplicated review/attack check separated,
and the response schema changed so material statements carry their citations.

A subsequent operator-run request reached Ready for review, all ten checks,
human approval and an audit decision. This is one successful demonstrated flow,
not a guarantee that every future model response will pass.

Do not respond to future failures by silently switching providers, removing
controls, inventing citations or labeling a fixture as live.

## Safe diagnostics

The current terminal diagnostic prints a finish reason and completion-token count.
It intentionally omits raw answers, prompt text, evidence and credentials.
The audit records safe event metadata and provider identifiers. Error screens
use application codes rather than raw upstream error bodies.

For help, share the run state, reason code, failed check names, configured model
name and safe metadata. Do not post `.env`, keys, cookies, client files, source bodies
or a database dump.

## Persistence and restart

The default database is `data/mattergate.sqlite3`. Ready and reviewed runs persist.
Active runs are marked blocked on startup. Seed initialization adds missing records
but does not silently replace versioned source content.

To demonstrate a clean first run, choose a new `MATTERGATE_DATABASE` path before
starting. Database copies contain questions, drafts and review rationales as well
as safe audit metadata; keep them local even though the seeded corpus is synthetic.

If a complete historical database is removed, its run history is lost. There is no
production backup/retention service or destructive reset API.
