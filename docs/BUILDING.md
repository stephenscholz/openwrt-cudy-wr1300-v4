# Build notes

## Build the current version

Linux with rootless Podman. Allow about 30 GiB of free disk space;
the first build compiles the toolchain and can take an hour or more.

```sh
sh build.sh
```

The default is six parallel jobs. Use `JOBS=4 sh build.sh` for fewer.
Images, checksums and build metadata go to `dist/`; the source tree and
logs stay in `_work/openwrt/`.

## What goes into this build

- OpenWrt tag `v25.12.6`, commit `64900e756efa667774214f9c6b17c113222e01f7`.
- The five feed revisions from that release's `feeds.conf.default`.
- [`0001-ramips-add-cudy-wr1300-v4.patch`](../patches/0001-ramips-add-cudy-wr1300-v4.patch).
- The packages in [`config.seed`](../config.seed).
- Debian bookworm, pinned by digest in [`Containerfile`](../Containerfile).

[`scripts/build.py`](../scripts/build.py) clones the source, applies the
patch, installs the feeds, runs `make defconfig`, downloads the sources
and builds the firmware. It checks the source/feed revisions and required
packages along the way.

`luci-app-weechat` is excluded from the feed installation because it causes
a Kconfig dependency cycle with these feed versions. It isn't included
in the firmware.

To check the output:

```sh
python3 scripts/verify.py dist
```

For a native build with OpenWrt's build dependencies installed:

```sh
python3 scripts/build.py --jobs 6
```

Add `--prepare-only` to check the source, patch, feeds and configuration
without compiling. There's also a manually started build under GitHub
Actions that uploads the output as artifacts.

## Updating to a newer OpenWrt release

1. In `scripts/build.py`, update `TAG`, `COMMIT` and `FEEDS` using the new
   release's source and `feeds.conf.default`.
2. Check whether the v4 patch still applies. Refresh it against the new
   source if needed; see [patch notes](../patches/README.md).
3. Review `config.seed`, and update the expected version in
   `scripts/verify.py`. Update the version in the GitHub Actions artifact
   name too.
4. Use a fresh work directory for the new version. Rename `_work/` and
   `dist/` to keep the previous build, then run `sh build.sh`.
5. Check the output with `scripts/verify.py` and test the sysupgrade image
   on the router. Update the README with what actually works.
6. Commit the changes and publish the release:

   ```sh
   VERSION=25.12.6
   git tag "v$VERSION"
   git push origin main "v$VERSION"
   gh release create "v$VERSION" dist/* --verify-tag --title "OpenWrt $VERSION" --notes-file release-notes.md
   ```

Set `VERSION` and update `release-notes.md` for that build before
running those commands. Upload the checksums, manifest and build metadata
alongside the images so the release records its inputs.

Pinned inputs help repeat the build, but different build environments
can still produce different binary checksums.
