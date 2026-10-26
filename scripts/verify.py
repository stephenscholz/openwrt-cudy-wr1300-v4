#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify release checksums, profile, size, package manifest and image header."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib


def verify(directory):
    for line in (directory / 'sha256sums').read_text().splitlines():
        expected, name = line.split(maxsplit=1)
        name = name.removeprefix('*')
        if Path(name).name != name:
            raise ValueError(f'Unexpected checksum path: {name}')
        actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f'Checksum mismatch: {name}')
    profiles = json.loads((directory / 'profiles.json').read_text())
    if profiles['version_number'] != '25.12.6' or profiles['target'] != 'ramips/mt7621':
        raise ValueError('Unexpected release or target')
    profile = profiles['profiles']['cudy_wr1300-v4']
    if set(profile['supported_devices']) != {'cudy,wr1300-v4', 'R98'}:
        raise ValueError('Unexpected supported devices')
    image = next(i for i in profile['images'] if i['type'] == 'sysupgrade')
    data = (directory / image['name']).read_bytes()
    if len(data) != image['size'] or len(data) >= profile['file_size_limits']['image']:
        raise ValueError('Invalid firmware size')
    if hashlib.sha256(data).hexdigest() != image['sha256']:
        raise ValueError('Image differs from profiles.json')
    # Legacy uImage header and kernel payload have independent CRC32 checks.
    magic, header_crc, _, kernel_size, _, _, kernel_crc = struct.unpack_from('>7I', data)
    if magic != 0x27051956:
        raise ValueError('Not a legacy uImage')
    header = bytearray(data[:64])
    header[4:8] = b'\0' * 4
    if zlib.crc32(header) != header_crc:
        raise ValueError('Invalid uImage header CRC')
    if zlib.crc32(data[64:64 + kernel_size]) != kernel_crc:
        raise ValueError('Invalid kernel payload CRC')
    manifest = (directory / 'openwrt-ramips-mt7621-cudy_wr1300-v4.manifest').read_text()
    packages = {line.split(' - ', 1)[0] for line in manifest.splitlines()}
    required = {'luci', 'luci-ssl', 'relayd', 'luci-proto-relay', 'iwinfo',
                'kmod-mt7603', 'kmod-mt7615e', 'kmod-mt7663-firmware-ap'}
    if not required <= packages:
        raise ValueError(f'Missing packages: {required - packages}')
    print(f'Checksums, WR1300 v4 profile, size, kernel CRCs and packages verified ({len(data):,} bytes).')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    verify(parser.parse_args().directory)
