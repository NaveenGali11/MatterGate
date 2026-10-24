# Repository and release publishing

Public source: [NaveenGali11/MatterGate](https://github.com/NaveenGali11/MatterGate).

Publishing source does not deploy the application. Follow [setup](setup.md) for
local use and [release guide](release-guide.md) for a source test build.

## Review a public revision

- Run the local tests, inspect the staged diff and check CI for the revision being published.
- Include source, tests, pinned dependencies, setup documentation and required licenses.
- Keep private configuration, databases, logs, caches, local plans and generated archives out of Git.
- Review screenshots for credentials and confidential content. The supplied gallery uses synthetic/public research material.
- Keep the PriviLAB source manifest and modification notices accurate when adapted code changes.

The ignore rules cover local runtime state and asset-generation working files.
They do not remove secrets from existing history. Only the placeholder
`.env.example` belongs in the repository.

## Suggested repository metadata

**Description**

Permissioned legal research using NVIDIA Nemotron on Nebius Token Factory, with
scoped evidence, human review and traceable run receipts.

**Topics**

`nebius`, `nemotron`, `nvidia`, `legaltech`, `fastapi`, `sqlite`,
`responsible-ai`, `hackathon`.

Use a website URL only when it points to an accessible project page or working demo.

## Verify publication

Check README images and links, source/static/seed assets, the MIT license,
PriviLAB Apache-2.0 notices and the Actions result. A local test pass is separate
from the remote workflow result. A source archive is separate from a hosted app.
