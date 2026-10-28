"""Check distributable links, attribution hashes and source archive integrity.

Run from the repository root. No network, application startup or inference calls.
"""
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from package_release import ROOT, build, release_files


def main():
    files = {relative.as_posix(): body for relative, body in release_files(ROOT)}
    errors = []
    documents = [name for name in files if name.endswith(".md")]
    for name in documents:
        text = files[name].decode("utf-8")
        references = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
        references += re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', text)
        for reference in references:
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = (ROOT / Path(name).parent / unquote(parsed.path)).resolve()
            if not target.is_relative_to(ROOT.resolve()):
                errors.append(f"{name}: link outside the source tree")
            elif target.relative_to(ROOT.resolve()).as_posix() not in files:
                errors.append(f"{name}: missing distributable target {reference}")

    manifest = json.loads(files["docs/upstream/privilab-manifest.json"])
    adaptations = {}
    for entry in manifest["files"]:
        adaptations.update(entry["local_sha256"])
    for name, expected in adaptations.items():
        if name not in files or hashlib.sha256(files[name]).hexdigest() != expected:
            errors.append(f"PriviLAB adaptation hash mismatch: {name}")
    for required in ("LICENSE", "third_party/privilab/LICENSE", "third_party/privilab/NOTICE"):
        if not files.get(required):
            errors.append(f"Missing license/notice: {required}")

    archive_path = build()
    with ZipFile(archive_path) as archive:
        if archive.testzip() is not None:
            errors.append("Archive failed its ZIP integrity check")
        recorded = json.loads(archive.read("mattergate/BUILD_MANIFEST.json"))
        expected_names = {"mattergate/" + name for name in files}
        expected_names.add("mattergate/BUILD_MANIFEST.json")
        if set(archive.namelist()) != expected_names or set(recorded["files"]) != set(files):
            errors.append("Archive file list does not match source projection")
        for name, body in files.items():
            if archive.read("mattergate/" + name) != body:
                errors.append(f"Archive content differs: {name}")
            if recorded["files"].get(name) != hashlib.sha256(body).hexdigest():
                errors.append(f"Archive hash differs: {name}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Passed: {len(documents)} Markdown files, local link/image targets, "
          f"{len(adaptations)} adaptation hashes, licenses and {len(files)} archive files.")
    print("SHA-256", hashlib.sha256(archive_path.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
