# Publish MatterGate to GitHub

This is a manual publication guide. No repository was created, committed, pushed,
made public or deployed while preparing this documentation.

## Before the first public commit

1. Run the latest local tests and inspect the result. The recorded 73-pass baseline
   predates the later changes; do not add a current passing badge without evidence.
2. Review the files you intend to stage. Keep `.env`, all local secret variants,
   session secrets, `.venv`, SQLite files, runtime data and logs out of Git.
3. Keep `.env.example`, `requirements.lock`, source, tests, documentation and all
   applicable license/NOTICE files.
4. Review screenshots for private content. The included images are the supplied
   synthetic demo screenshots, not captures of the Nebius key screen.
5. Confirm source attribution and `docs/upstream/privilab-manifest.json` remain
   accurate if adapted source changes.
6. Choose a repository name such as `mattergate` and create an empty GitHub repository.
   Use a public repository for the eventual hackathon submission. Do not initialize
   a second README or different license over the files already prepared here.

`.gitignore` prevents future untracked files from being added; it does not remove
a secret that was already committed. If credentials were ever published, revoke
them and repair the history separately.

## Suggested repository metadata

**Description**

Permissioned legal research using NVIDIA Nemotron on Nebius Token Factory, with
scoped evidence, deterministic checks, human review and an audit trail.

**Topics**

`nebius`, `nemotron`, `nvidia`, `legaltech`, `ai-agents`, `fastapi`,
`sqlite`, `responsible-ai`, `hackathon`.

Do not add a public website URL until it points to an actual accessible demo.

## Commands for you to execute

From the project root, inspect whether Git is already initialized:

~~~sh
git status
~~~

If it is not a Git repository, initialize it:

~~~sh
git init -b main
~~~

Stage the known publication files explicitly:

~~~sh
git add .gitignore .env.example pyproject.toml requirements.lock LICENSE README.md CHANGELOG.md CONTRIBUTING.md SECURITY.md BUILD_PLAN.md mattergate-prd.md app tests docs third_party .github
git status --short
git diff --cached --stat
~~~

Before committing, confirm no private files are tracked:

~~~sh
git ls-files -- '.env' '.env.*' '*.sqlite3*' 'data/*' '*.log'
~~~

`.env.example` is expected in that output. An actual `.env`, key backup, runtime log
or database is not. Inspect unexpected results before publishing.

After reviewing the staged content:

~~~sh
git commit -m "Build MatterGate permissioned research MVP"
~~~

If this checkout already has a remote, inspect it before changing anything:

~~~sh
git remote -v
~~~

For a new repository with no origin, replace the placeholder below with the
exact URL GitHub gives you:

~~~sh
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/mattergate.git
git push -u origin main
~~~

Do not force-push or overwrite an existing repository to follow this example.
If the existing branch has a different name, use that branch deliberately or
rename it after reviewing the repository's history.

## Verify the published result

- Open the repository and confirm README links, screenshots, Mermaid diagrams
  and the license render.
- Check that source, tests, fixture JSON, prompt text, SQL and static assets exist.
- Confirm the Apache license/NOTICE and source manifest are present.
- Inspect GitHub Actions; record the actual latest result.
- Verify `.env`, databases, logs and credentials are absent.
- Save the actual repository URL for the submission form.

Publishing the repository does not deploy the app. Judge access and the public
demo video are separate deliverables; see [submission brief](hackathon-submission.md).
