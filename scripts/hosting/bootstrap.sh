#!/bin/sh
# Ubuntu 24.04 host setup. Contains no credentials or application data.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y python3-venv caddy unzip ca-certificates
id mattergate >/dev/null 2>&1 || useradd --system --home-dir /var/lib/mattergate --shell /usr/sbin/nologin mattergate
install -d -m 0755 /opt/mattergate/releases
install -d -m 0700 -o mattergate -g mattergate /var/lib/mattergate /var/lib/mattergate/backups
install -d -m 0700 /etc/mattergate
if ! swapon --show | grep -q /swapfile; then
    if [ ! -f /swapfile ]; then
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
    fi
    swapon /swapfile
    grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi
echo 'MatterGate host bootstrap complete'
