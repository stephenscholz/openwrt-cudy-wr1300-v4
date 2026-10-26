# OpenWrt for Cudy WR1300 v4

My build of **OpenWrt 25.12.6** for the WR1300 v4. Includes LuCI with
HTTPS, relayd and iwinfo. Kernel 6.12.112.

I upgraded my router from OpenWrt 23.05.5 with settings retained.
5 GHz client mode with WPA3 works. I haven't tested 2.4 GHz, AP mode,
Ethernet forwarding, IPv6, LEDs/buttons or recovery yet.

## Download & install

**[Download firmware](https://github.com/stephenscholz/openwrt-cudy-wr1300-v4/releases/latest)**

For **WR1300 v4 already running OpenWrt**. Use the
`squashfs-sysupgrade.bin` file, not `initramfs-kernel.bin`.
Installation from Cudy stock firmware isn't covered here.

Back up your settings, then upload the image in
**LuCI → System → Backup / Flash Firmware**. Or copy it to
`/tmp/firmware.bin` and run:

```sh
sysupgrade -T /tmp/firmware.bin && sysupgrade /tmp/firmware.bin
```

Don't force the upgrade if the compatibility check fails.

## Build

On Linux with rootless Podman:

```sh
git clone https://github.com/stephenscholz/openwrt-cudy-wr1300-v4.git
cd openwrt-cudy-wr1300-v4
sh build.sh
```

Images end up in `dist/`. [Build notes and updating to a newer release](docs/BUILDING.md).

## Thanks

Jan Brudna, zekica and GuoShuangyan for the device-support work linked in
[OpenWrt #22082](https://github.com/openwrt/openwrt/issues/22082).
[Patch details](patches/README.md).

This is my own build, not an official OpenWrt release.
Build scripts: [GPL-2.0](LICENSE). Firmware packages keep their upstream licenses.
