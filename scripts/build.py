#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the pinned OpenWrt release with the bundled WR1300 v4 patch."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '_work/openwrt'
TAG = 'v25.12.6'
COMMIT = '64900e756efa667774214f9c6b17c113222e01f7'
PATCH = ROOT / 'patches/0001-ramips-add-cudy-wr1300-v4.patch'
FEEDS = {
    'packages': '093d551675b1119a06ef224d419905e8d6b2af1a',
    'luci': '75a306df84a020c57a631ef5b4c02ace56d93387',
    'routing': '48c808034414a2112cf9d5261a20a320e8d0d170',
    'telephony': '2618106d5846a4a542fdf5809f0d3ed228ce439b',
    'video': '094bf58da6682f895255a35a84349a79dab4bf95',
}


def run(*args, cwd=SOURCE, **kwargs):
    print('+ ' + ' '.join(map(str, args)), flush=True)
    return subprocess.run(list(map(str, args)), cwd=cwd, check=True, **kwargs)


def git_head(path):
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=path, text=True).strip()


def build(jobs, prepare_only=False):
    SOURCE.parent.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists():
        run('git', 'clone', '--depth', '1', '--branch', TAG,
            'https://github.com/openwrt/openwrt.git', SOURCE, cwd=ROOT)
    if git_head(SOURCE) != COMMIT:
        raise RuntimeError(f'{SOURCE} must be at {COMMIT}; use a fresh work directory')
    marker = SOURCE / '.wr1300-v4-patch.sha256'
    digest = hashlib.sha256(PATCH.read_bytes()).hexdigest()
    if marker.exists():
        if marker.read_text().strip() != digest:
            raise RuntimeError('Patch changed; use a fresh work directory')
        run('git', 'apply', '--reverse', '--check', PATCH)
    else:
        run('git', 'apply', '--check', PATCH)
        run('git', 'apply', PATCH)
        marker.write_text(digest + '\n')
    run('git', 'diff', '--check')
    run('./scripts/feeds', 'update', '-a')
    for name, revision in FEEDS.items():
        if git_head(SOURCE / 'feeds' / name) != revision:
            raise RuntimeError(f'Unexpected {name} feed revision')
    run('./scripts/feeds', 'install', '-a')
    # The release's pinned feeds contain a Kconfig cycle in this unrelated app.
    run('./scripts/feeds', 'uninstall', 'luci-app-weechat')
    shutil.copyfile(ROOT / 'config.seed', SOURCE / '.config')
    run('make', 'defconfig')
    config = set((SOURCE / '.config').read_text().splitlines())
    required = {
        'CONFIG_TARGET_ramips_mt7621_DEVICE_cudy_wr1300-v4=y',
        'CONFIG_PACKAGE_luci=y', 'CONFIG_PACKAGE_luci-ssl=y',
        'CONFIG_PACKAGE_luci-proto-relay=y', 'CONFIG_PACKAGE_relayd=y',
        'CONFIG_PACKAGE_iwinfo=y', 'CONFIG_PACKAGE_kmod-mt7603=y',
        'CONFIG_PACKAGE_kmod-mt7615e=y',
        'CONFIG_PACKAGE_kmod-mt7663-firmware-ap=y',
    }
    if not required <= config:
        raise RuntimeError(f'Missing configuration: {required - config}')
    if prepare_only:
        print('Pinned source, patch, feed revisions and configuration verified.', flush=True)
        return
    run('make', f'-j{jobs}', 'download')
    run('make', f'-j{jobs}', 'BUILD_LOG=1')
    output = SOURCE / 'bin/targets/ramips/mt7621'
    run('sha256sum', '-c', 'sha256sums', cwd=output)
    metadata = json.loads(subprocess.check_output([
        str(SOURCE / 'staging_dir/host/bin/fwtool'), '-i', '/dev/stdout',
        str(output / 'openwrt-ramips-mt7621-cudy_wr1300-v4-squashfs-sysupgrade.bin')]))
    if metadata['version']['board'] != 'cudy_wr1300-v4':
        raise RuntimeError('Incorrect board in embedded firmware metadata')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    for path in output.iterdir():
        if path.is_file():
            shutil.copyfile(path, dist / path.name)
    run('python3', ROOT / 'scripts/verify.py', dist, cwd=ROOT)
    print(f'Firmware and checksums are in {dist}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--jobs', type=int, default=6)
    parser.add_argument('--prepare-only', action='store_true',
                        help='verify source, patch, feeds and configuration without compiling firmware')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    build(args.jobs, args.prepare_only)
