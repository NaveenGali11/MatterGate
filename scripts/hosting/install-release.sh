#!/usr/bin/env bash
# Usage: sudo bash install-release.sh /tmp/mattergate-test-build.zip release-id hostname
# /etc/mattergate/environment must be installed separately with mode 0600.
set -euo pipefail
archive=$1
release_id=$2
hostname=$3
[[ "$release_id" =~ ^[a-zA-Z0-9_-]+$ ]]
[[ "$hostname" =~ ^[a-zA-Z0-9.-]+$ ]]
release_dir="/opt/mattergate/releases/$release_id"
test ! -e "$release_dir"
install -d "$release_dir"
unzip -q "$archive" -d "$release_dir/unpack"
mv "$release_dir/unpack/mattergate/"* "$release_dir/"
rm -rf "$release_dir/unpack"
python3 -m venv "$release_dir/.venv"
"$release_dir/.venv/bin/pip" install --disable-pip-version-check -q -r "$release_dir/requirements.lock"
"$release_dir/.venv/bin/pip" install --disable-pip-version-check -q --no-deps "$release_dir"
"$release_dir/.venv/bin/python" -c 'import sqlite3; c=sqlite3.connect(":memory:"); c.execute("CREATE VIRTUAL TABLE check_fts USING fts5(text)"); print("SQLite FTS5 ready")'
ln -sfn "$release_dir" /opt/mattergate/current
install -m 0644 "$release_dir/scripts/hosting/mattergate.service" /etc/systemd/system/
install -m 0644 "$release_dir/scripts/hosting/mattergate-backup.service" /etc/systemd/system/
install -m 0644 "$release_dir/scripts/hosting/mattergate-backup.timer" /etc/systemd/system/
sed "s/__HOSTNAME__/$hostname/g" "$release_dir/scripts/hosting/Caddyfile.template" > /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile
systemctl daemon-reload
systemctl enable --now mattergate mattergate-backup.timer caddy
systemctl restart mattergate
systemctl reload caddy
