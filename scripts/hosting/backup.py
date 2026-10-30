"""Create a consistent local SQLite backup for inclusion in daily host snapshots."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

root = Path("/var/lib/mattergate")
backups = root / "backups"
backups.mkdir(mode=0o700, exist_ok=True)
target = backups / (datetime.now(timezone.utc).strftime("%Y-%m-%d") + ".sqlite3")
with sqlite3.connect(f"file:{root / 'mattergate.sqlite3'}?mode=ro", uri=True) as source:
    with sqlite3.connect(target) as destination:
        source.backup(destination)
        if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Backup integrity check failed")
for old in sorted(backups.glob("*.sqlite3"))[:-7]:
    old.unlink()
print("Daily database backup verified")
