"""Build a reproducible source test-build archive without private local state.

Run from the repository root: .venv/bin/python scripts/package_release.py
This packages source only. It does not run the application or make network calls.
"""
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {"README.md", "HANDOVER.md", "LICENSE", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md",
              "BUILD_PLAN.md", "mattergate-prd.md", "pyproject.toml", "requirements.lock", ".env.example", ".gitignore"}
DIRECTORIES = {"app", "docs", "tests", "third_party", ".github", "scripts"}


def release_files(root):
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        # Never descend via symlink, include a hidden local directory, or package caches.
        if any(part.startswith(".") and part != ".github" for part in relative.parts[:-1]):
            continue
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if relative.parts[:2] in {("docs", "upgrades"), ("docs", "archive")}:
            continue
        if path.name.endswith(".prompt.txt"):
            continue
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root.parent):
            continue
        if not path.is_file():
            continue
        if len(relative.parts) == 1:
            if relative.name not in ROOT_FILES:
                continue
        elif relative.parts[0] not in DIRECTORIES:
            continue
        if path.name.startswith(".env") and relative.as_posix() != ".env.example":
            continue
        if path.suffix in {".log", ".sqlite3", ".db", ".pem", ".key"} or ".sqlite3" in path.name:
            continue
        yield relative, path.read_bytes()


def build(root=ROOT):
    destination = root / "dist/mattergate-test-build.zip"
    destination.parent.mkdir(exist_ok=True)
    files = list(release_files(root))
    manifest = {"format":"mattergate-source-test-build-v1", "files":{
        path.as_posix():hashlib.sha256(body).hexdigest() for path,body in files}}
    files.append((Path("BUILD_MANIFEST.json"),(json.dumps(manifest,indent=2)+"\n").encode()))
    with ZipFile(destination,"w",compression=ZIP_DEFLATED) as archive:
        for relative, body in files:
            info = ZipInfo("mattergate/"+relative.as_posix(), date_time=(2026,10,24,0,0,0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info,body)
    return destination


if __name__ == "__main__":
    destination = build()
    print(destination)
    print("SHA-256",hashlib.sha256(destination.read_bytes()).hexdigest())
