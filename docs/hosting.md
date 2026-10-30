# Public AWS demo

The synthetic MatterGate demo is available at:

**[Open MatterGate](https://mattergate-34-225-81-63.sslip.io)**

Verified October 30, 2026. The temporary hostname uses third-party sslip.io DNS
and an attached AWS static IP; it is not an owned custom domain. No account or
API key is required from visitors. Demo roles remain simulated.

## Using the hosted version

1. Choose **Run allowed assessment** for the live NVIDIA/Nebius workflow.
2. Inspect the brief and select an evidence reference.
3. Open **Human review**, continue as Alex, and record a decision on the research draft.
4. Open **Run receipt** for measured operations, provider diagnostics and safe JSON export.
5. Return to Overview and choose **See the blocked request** to demonstrate denial before retrieval or inference.

Each browser session owns its workspace. Other visitors cannot list, read, export
or review its runs by choosing the same demo role. Use the same browser session
throughout a recording. A cleared cookie, private browsing window, different
browser, or expired eight-hour session starts a separate workspace; there is no
account-based recovery. Do not enter real client, personal or confidential data.

Live generation has a shared allowance. **New research → Fixture** remains an
explicit no-inference alternative for the exact prefilled EU vendor question.
The app never silently substitutes a saved fixture for a live response.

## Deployment shape and cost

- Amazon Lightsail Linux, `us-east-1`, 1 GB RAM / 40 GB disk / public IPv4 bundle.
- Caddy terminates HTTPS and forwards to one Uvicorn worker on loopback.
- systemd starts and supervises the process; SQLite lives outside release directories.
- Application runtime calls Nebius directly and receives no AWS credentials.
- Daily consistent SQLite backups are included in daily host snapshots.

The starting instance list price is **$7/month**, with snapshots metered separately.
The initial AWS planning allowance is **$8–$10/month**, excluding taxes, excess
transfer, custom domains and Nebius usage. A USD 15 Lightsail budget provides
notifications, not an immediate billing cutoff. Check [AWS pricing](https://aws.amazon.com/lightsail/pricing/)
before creating resources; eligibility for credits is account-specific.

This is a low-traffic, single-server demonstration. It is not a highly available
or authenticated business deployment. A larger instance, remote database and
durable work queue require separate capacity planning.

## Public-mode controls

Enable public mode explicitly; local development preserves its existing behavior.

| Setting | Hosted value / purpose |
|---|---|
| `MATTERGATE_PUBLIC_DEMO` | `true`: browser-workspace checks, admission limits, Secure cookies and host validation |
| `MATTERGATE_PUBLIC_ORIGIN` | Exact HTTPS origin, without a trailing slash |
| `MATTERGATE_DATABASE` | `/var/lib/mattergate/mattergate.sqlite3` |
| `MATTERGATE_SESSION_SECRET` | Stable random server secret; at least 32 characters |
| `MATTERGATE_LIVE_ENABLED` | `true`; set `false` and restart to pause live inference |
| `MATTERGATE_LIVE_DAILY_LIMIT` | `100` actual provider HTTP attempts per UTC day |
| `MATTERGATE_LIVE_MONTHLY_LIMIT` | `1000` actual provider HTTP attempts per UTC month |

Attempt reservations are transactional and persistent, including malformed-output
retries. These are attempt limits, not currency limits. Per-session requests are
limited to six/minute; public mode also limits each client IP to twenty/minute.
The initial cap is four active runs, two simultaneous live generations and 2,000
stored runs. Busy/quota cases stop explicitly. There is no automatic purge of
immutable audit/review records.

## Reproduce the host setup

Provision an Ubuntu 24.04 Lightsail instance with a dedicated administration
identity, an attached static IPv4 and a hostname resolving to it. Allow public
TCP 80/443; restrict TCP 22 to the operator. Keep port 8000 private. The default
Lightsail user-data wrapper invokes `/bin/sh`, so the bootstrap is POSIX-compatible.

Host configuration lives under [scripts/hosting](../scripts/hosting/bootstrap.sh):

1. Run `bootstrap.sh` as root to install Python, Caddy and an unprivileged service user.
2. Build the archive locally with `python scripts/check_release.py` and transfer it over SSH.
3. Securely install `/etc/mattergate/environment` as root, mode `0600`, using
   the settings above and the server-only Nebius configuration from `.env.example`.
   Never put secrets in user data, Git, shell arguments or the source archive.
4. Run `install-release.sh` as root with the archive path, a unique release ID,
   and the public hostname. It installs pinned dependencies, checks FTS5, validates
   Caddy and enables the systemd service and backup timer.
5. Enable Lightsail automatic snapshots at 02:00 UTC. The consistent SQLite backup
   timer runs at 01:00 UTC. Preserve Caddy's certificate storage across updates.
6. Verify HTTPS, host/origin checks, two isolated browser sessions, the live path,
   denial, review, receipt export, restart persistence and backup restoration.

The source archive deliberately excludes local databases, secrets, SSH keys,
private deployment state and private planning documents. Start with a fresh
hosted database seeded from the repository.

## Operations, rollback and removal

The release link is `/opt/mattergate/current`; immutable release directories live
under `/opt/mattergate/releases/`. Application state is `/var/lib/mattergate/` and
private environment configuration is `/etc/mattergate/environment`.

Useful commands after an authorized SSH connection:

```sh
sudo systemctl status mattergate caddy
sudo journalctl -u mattergate -n 50 --no-pager
sudo systemctl start mattergate-backup.service
curl --fail https://YOUR_HOSTNAME/healthz
```

`GET /healthz` checks the local database; it makes no provider call. Logs should
contain safe codes/metadata, never environment-file contents. The backup helper
uses SQLite's online backup API, verifies database integrity and retains seven
dated local backups. Lightsail retains the latest seven automatic snapshots.
Backup recovery can lose up to one day of writes and requires an operator.

For a compatible code rollback, point `current` at a known working release and
restart `mattergate`. Before schema changes, take a consistent backup; an
incompatible rollback requires the matching database backup and a deliberate
decision about intervening writes. Do not use multiple Uvicorn workers or servers
against separate copies of this SQLite database. Restarting blocks interrupted
active runs; it does not transparently resume inference.

To stop charges after the demo is no longer needed, export any required records,
then remove the dedicated instance, snapshots and unused static IP. **Stopping a
Lightsail instance does not stop its instance charges.** Remove the dedicated
budget only after reviewing final billing. Preserve the public demo throughout
the submission's required judging window.

## Recorded acceptance

October 30 verification:

- 108 automated tests pass locally (Python 3.14) and on the Ubuntu host (Python 3.12).
- Public HTTPS requests, Secure cookies and CSRF rejection/acceptance pass.
- Two independent browser clients cannot access each other's history, run data,
  review mutation or receipt export, including after switching to Alex.
- A real hosted Nemotron request returned HTTP 200 / finish reason `stop` and
  passed 10/10 controls. An additional browser-driven live run was reviewed.
- Restricted research measured zero retrieval and provider attempts.
- Approved fixture history and live receipts survived a service restart.
- A consistent backup restored to an isolated database with valid audit chains.

These are acceptance observations, not a sustained-load benchmark, external
security audit or validation of legal accuracy. One existing Starlette/HTTPX
test-client deprecation warning remains.
