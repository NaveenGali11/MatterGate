import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile


def test_test_build_excludes_local_package_and_private_state(tmp_path):
    source = Path(__file__).resolve().parents[1]/"scripts/package_release.py"
    spec = importlib.util.spec_from_file_location("package_release",source)
    package = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(package)
    for name in ("README.md","HANDOVER.md",".env.example","app/main.py","docs/setup.md",".github/workflows/tests.yml",
                 ".env","app/.env.local","data/state.sqlite3","docs/upgrades/README.md",".venv/lib/secret.py",
                 "app/__pycache__/cached.pyc","docs/debug.log","app/private.key","app/old.sqlite3-wal",
                 "docs/archive/mattergate-prd-v1.md","docs/images/devpost/mattergate-thumbnail.prompt.txt",
                 "matter_gate_thumbnail.png"):
        file = tmp_path/name; file.parent.mkdir(parents=True,exist_ok=True); file.write_text(name)
    (tmp_path/"app/linked.py").symlink_to(tmp_path/".env")
    result = package.build(tmp_path)
    original = result.read_bytes()
    assert package.build(tmp_path).read_bytes() == original
    with ZipFile(result) as archive:
        names = set(archive.namelist())
        assert names == {"mattergate/"+name for name in ("README.md","HANDOVER.md",".env.example","app/main.py","docs/setup.md",
            ".github/workflows/tests.yml","BUILD_MANIFEST.json")}
        manifest = json.loads(archive.read("mattergate/BUILD_MANIFEST.json"))
        assert len(manifest["files"]) == 6
