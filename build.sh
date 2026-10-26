#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-only
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
podman build -t localhost/openwrt-wr1300-v4-builder -f "$ROOT/Containerfile" "$ROOT"
podman run --rm --userns=keep-id --user "$(id -u):$(id -g)" \
    -e HOME=/tmp -v "$ROOT:/workspace:Z" \
    localhost/openwrt-wr1300-v4-builder \
    python3 scripts/build.py --jobs "${JOBS:-6}"
