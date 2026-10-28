# Local setup

## Requirements

Use Python 3.14 for the development environment closest to the recorded baseline.
The project declares Python 3.12+, but other versions/platforms have not all been
tested. SQLite must include FTS5. The UI needs no Node build step.

Use a single worker and localhost. The app is a synthetic demo with selectable
identities, not a public production service.

## Install

Clone or download the repository. For a new checkout:

~~~sh
git clone https://github.com/NaveenGali11/MatterGate.git
cd MatterGate
~~~

Then install the pinned dependencies:

~~~sh
uv venv --python python3
uv pip install --python .venv/bin/python -r requirements.lock -e .
~~~

If you do not use uv:

~~~sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock -e .
~~~

The lock was resolved on macOS/Python 3.14 and has also been installed by the
passing Ubuntu/Python 3.14 CI workflow. It pins runtime and development dependencies;
it is not a guarantee for every Python version or platform.

## Configure

If a local `.env` does not already exist, copy `.env.example` to `.env` using your
editor or file manager. Preserve an existing configured file.

Generate a session secret:

~~~sh
.venv/bin/python -c "import secrets; print(secrets.token_urlsafe(48))"
~~~

Paste it into `MATTERGATE_SESSION_SECRET`. Do not publish it.

| Variable | Default / bound | Purpose |
|---|---|---|
| `MATTERGATE_DATABASE` | `data/mattergate.sqlite3` | Local database path |
| `MATTERGATE_SESSION_SECRET` | Random per process when absent | Signs demo sessions; set a persistent private value to survive restarts |
| `NEBIUS_API_KEY` | Empty | Required for live attempts; leave blank for fixture use |
| `NEBIUS_BASE_URL` | `https://api.tokenfactory.nebius.com/v1` | Allowed Nebius HTTPS API base |
| `NEBIUS_MODEL` | `nvidia/Nemotron-3_5-Lightning` | NVIDIA model identifier |
| `MODEL_TIMEOUT_SECONDS` | 45; bounded to 1–45 | Total live-generation budget, including repair |
| `MODEL_MAX_OUTPUT_TOKENS` | 900; bounded to 128–900 | Provider output cap |
| `MODEL_TEMPERATURE` | 0.1; bounded to 0–1 | Generation setting |

Environment variables take precedence over `.env` values. Restart after changing
configuration. Increasing `MODEL_MAX_OUTPUT_TOKENS` above 900 does not override
the application's cap.

Allowed hosts are `api.tokenfactory.nebius.com` and
`api.tokenfactory.us-central1.nebius.com`. The URL must use HTTPS, standard port,
`/v1`, and no embedded credentials, query or fragment. A different cloud/provider
URL is intentionally rejected.

The current Lightning configuration was used successfully in the operator's live
walkthrough. The regional Super configuration is retained as a supported option,
but changing models can change output quality, latency and feature support.
Thinking is requested off for the recognized Lightning/Super identifiers.

## Start

~~~sh
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
~~~

Visit [the app](http://127.0.0.1:8000/) and
[system status](http://127.0.0.1:8000/status). Startup creates the database and seeds
three users, a policy and six sources. Explicit seeding is also available:

~~~sh
.venv/bin/python -m app.seed
~~~

Seeding is idempotent: it does not replace existing source versions or decisions.
For a fresh demonstration, set `MATTERGATE_DATABASE` to a new file path and restart.
Do not delete an audit database just to hide a failed run.

Keep the terminal open; Ctrl+C stops the app. Only one worker should operate this
demo database. Restarted active runs are marked `BLOCKED / PROCESS_INTERRUPTED`.

## Live or fixture

With no key, fixture mode works for the exact seeded EU vendor question.
With valid configuration, scenario buttons use live mode; the custom form lets
you explicitly choose an available mode. A badge is configuration information,
not proof that a request succeeded.

A completed live run exposes provider/model, latency, attempt count and an ID when
the provider supplied one. The terminal diagnostic prints only finish reason and
output-token count. It does not print the answer, prompt or credentials.

See [operations](operations.md) for failure codes and
[user guide](user-guide.md) for the review/denial demonstration.
