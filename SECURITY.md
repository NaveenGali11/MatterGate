# Security scope and reporting

MatterGate is a local demonstration using synthetic/public materials. It is not
a production authentication, legal-advice, privilege or compliance system.

## Use within the intended boundary

- Bind the demo server to localhost and use one worker.
- Keep all questions, documents and rationale synthetic.
- Keep Nebius keys and session secrets server-side in an ignored `.env`.
- Do not commit runtime databases, logs, cookies, key screenshots or environment backups.
- Do not expose the app to untrusted users as a production service: demo identities
  can be freely switched and do not authenticate a real person.

Implemented controls and known limitations are described in
[the threat model](docs/threat-model.md). The local event hash chain is not an
external trust anchor, and string/citation checks do not establish legal accuracy
or comprehensive prompt-injection resistance.

## Report privately

If a vulnerability or exposed credential is found, contact the repository owner
using a private channel listed on their GitHub profile or GitHub's private
vulnerability reporting feature if enabled. No dedicated reporting email or
response-time commitment has been established.

Do not open a public issue containing an exploit with private data, an API key,
an environment file or a database dump. A useful sanitized report includes the
affected revision, component, reproduction with synthetic data and observed impact.

If a credential was exposed, revoke/rotate it with the provider rather than
relying only on deletion of the visible file. The repository does not implement
automated incident response, production retention or secret recovery.
